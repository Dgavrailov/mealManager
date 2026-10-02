"""Authentication and session management — stdlib only."""

import hashlib
import os
import secrets
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import config
from repo.database import Database


_PBKDF2_ITERATIONS = 200_000


def _hash_password(password: str, salt: str) -> str:
    """New/updated passwords use PBKDF2-HMAC-SHA256 with a real work factor.

    Format 'pbkdf2$<iterations>$<hex>' is self-describing so _verify_password
    can still check old plain-SHA256 hashes (no '$') without a schema change.
    """
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ITERATIONS).hex()
    return f"pbkdf2${_PBKDF2_ITERATIONS}${digest}"


def _verify_password(password: str, salt: str, stored_hash: str) -> bool:
    if stored_hash.startswith("pbkdf2$"):
        _, iterations, _ = stored_hash.split("$", 2)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations)).hex()
        expected = f"pbkdf2${iterations}${digest}"
    else:
        expected = hashlib.sha256((salt + password).encode()).hexdigest()
    return secrets.compare_digest(expected, stored_hash)


def _new_salt() -> str:
    return secrets.token_hex(16)


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _expires(hours: int = 1) -> str:
    return (datetime.utcnow() + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")


class AuthService:
    SESSION_HOURS = 72   # sessions last 3 days
    RESET_HOURS   = 1    # reset links expire in 1 hour

    def __init__(self, db: Database):
        self._db = db

    # ── registration ─────────────────────────────────────────────────────────

    def register(self, username: str, email: str, password: str) -> dict:
        """Create a new user. Returns the user dict or raises ValueError."""
        username = username.strip()
        email    = email.strip().lower()
        if not username or not email or not password:
            raise ValueError("Username, email and password are required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")

        salt = _new_salt()
        pw_hash = _hash_password(password, salt)

        with self._db.connect() as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE username=? OR email=?", (username, email)
            ).fetchone()
            if existing:
                raise ValueError("Username or email already registered.")
            cur = conn.execute(
                "INSERT INTO users (username, email, password_hash, salt) VALUES (?,?,?,?)",
                (username, email, pw_hash, salt),
            )
            user_id = cur.lastrowid

        return {"id": user_id, "username": username, "email": email}

    # ── login / logout ────────────────────────────────────────────────────────

    def login(self, username_or_email: str, password: str) -> Optional[str]:
        """Verify credentials and return a session token, or None on failure."""
        ident = username_or_email.strip().lower()
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT id, password_hash, salt FROM users WHERE lower(username)=? OR lower(email)=?",
                (ident, ident),
            ).fetchone()
            if row is None:
                return None
            if not _verify_password(password, row["salt"], row["password_hash"]):
                return None
            if not row["password_hash"].startswith("pbkdf2$"):
                # Transparently upgrade a legacy plain-SHA256 hash now that we know the password.
                conn.execute(
                    "UPDATE users SET password_hash=? WHERE id=?",
                    (_hash_password(password, row["salt"]), row["id"]),
                )
            token = secrets.token_urlsafe(32)
            conn.execute(
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (?,?,?)",
                (token, row["id"], _expires(hours=self.SESSION_HOURS)),
            )
        return token

    def logout(self, token: str) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))

    def get_user_by_token(self, token: str) -> Optional[dict]:
        """Return user dict if token is valid and not expired, else None."""
        if not token:
            return None
        with self._db.connect() as conn:
            row = conn.execute(
                """SELECT u.id, u.username, u.email
                   FROM sessions s JOIN users u ON s.user_id = u.id
                   WHERE s.token=? AND s.expires_at > datetime('now')""",
                (token,),
            ).fetchone()
        if row is None:
            return None
        return {"id": row["id"], "username": row["username"], "email": row["email"]}

    # ── password reset ────────────────────────────────────────────────────────

    def request_password_reset(self, email: str, base_url: str = "") -> bool:
        """Generate a reset token and send an email. Returns True if email found."""
        email = email.strip().lower()
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT id, username FROM users WHERE lower(email)=?", (email,)
            ).fetchone()
            if row is None:
                return False
            user_id  = row["id"]
            username = row["username"]

            # Invalidate any previous unused tokens for this user
            conn.execute(
                "DELETE FROM password_resets WHERE user_id=? AND used=0", (user_id,)
            )
            token = secrets.token_urlsafe(32)
            conn.execute(
                "INSERT INTO password_resets (token, user_id, expires_at) VALUES (?,?,?)",
                (token, user_id, _expires(hours=self.RESET_HOURS)),
            )

        reset_url = f"{base_url}/reset?token={token}"
        self._send_reset_email(email, username, reset_url)
        return True

    def reset_password(self, token: str, new_password: str) -> bool:
        """Apply a new password using a valid reset token. Returns True on success."""
        if len(new_password) < 6:
            raise ValueError("Password must be at least 6 characters.")
        with self._db.connect() as conn:
            row = conn.execute(
                """SELECT user_id FROM password_resets
                   WHERE token=? AND used=0 AND expires_at > datetime('now')""",
                (token,),
            ).fetchone()
            if row is None:
                return False
            user_id = row["user_id"]
            salt    = _new_salt()
            pw_hash = _hash_password(new_password, salt)
            conn.execute(
                "UPDATE users SET password_hash=?, salt=? WHERE id=?",
                (pw_hash, salt, user_id),
            )
            conn.execute(
                "UPDATE password_resets SET used=1 WHERE token=?", (token,)
            )
            # Invalidate all sessions so the user must log in again
            conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        return True

    def validate_reset_token(self, token: str) -> bool:
        with self._db.connect() as conn:
            row = conn.execute(
                """SELECT token FROM password_resets
                   WHERE token=? AND used=0 AND expires_at > datetime('now')""",
                (token,),
            ).fetchone()
        return row is not None

    # ── email ─────────────────────────────────────────────────────────────────

    def _send_reset_email(self, to_email: str, username: str, reset_url: str) -> None:
        if not config.SMTP_USER or config.SMTP_USER == "your_gmail@gmail.com":
            # SMTP not configured — print the link so the user can still test
            print(f"[AUTH] Password reset link for {to_email}: {reset_url}")
            return

        subject = "Meal Manager — password reset"
        body_text = (
            f"Hi {username},\n\n"
            f"Someone requested a password reset for your Meal Manager account.\n\n"
            f"Click the link below to set a new password (valid for 1 hour):\n\n"
            f"  {reset_url}\n\n"
            f"If you did not request this, you can safely ignore this email.\n\n"
            f"— Meal Manager"
        )
        body_html = f"""<html><body>
<p>Hi <strong>{username}</strong>,</p>
<p>Someone requested a password reset for your Meal Manager account.</p>
<p>Click the button below to set a new password (valid for <strong>1 hour</strong>):</p>
<p><a href="{reset_url}" style="background:#0d6efd;color:#fff;padding:10px 20px;
   border-radius:6px;text-decoration:none;display:inline-block;">Reset my password</a></p>
<p>If you did not request this, you can safely ignore this email.</p>
<p>— Meal Manager</p>
</body></html>"""

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = config.SMTP_FROM
        msg["To"]      = to_email
        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        ctx = ssl.create_default_context()
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ctx)
            smtp.login(config.SMTP_USER, config.SMTP_PASS)
            smtp.sendmail(config.SMTP_FROM, to_email, msg.as_string())
