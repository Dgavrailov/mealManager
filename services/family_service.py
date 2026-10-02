"""Family sharing service — stdlib only.

Two or more users can share a single data pool by joining a family group.
The owner creates the group and invites others by email.
When a user accepts, all their data queries are redirected to the owner's user_id,
so both see and modify the same meals, recipes, shopping list and weekly menu.
"""

from typing import List, Optional
from repo.database import Database


class FamilyService:
    def __init__(self, db: Database):
        self._db = db

    # ── helpers ───────────────────────────────────────────────────────────────

    def get_effective_user_id(self, user_id: int) -> int:
        """Return the owner's user_id if this user is in an active family group,
        otherwise return the user's own id."""
        with self._db.connect() as conn:
            row = conn.execute(
                """SELECT fg.owner_id
                   FROM family_members fm
                   JOIN family_groups fg ON fm.group_id = fg.id
                   WHERE fm.user_id = ? AND fm.status = 'active'
                   ORDER BY fm.invited_at
                   LIMIT 1""",
                (user_id,),
            ).fetchone()
        if row and row["owner_id"] != user_id:
            return row["owner_id"]
        return user_id

    # ── group management ──────────────────────────────────────────────────────

    def get_my_group(self, user_id: int) -> Optional[dict]:
        """Return the family group this user owns or belongs to, or None."""
        with self._db.connect() as conn:
            row = conn.execute(
                """SELECT fg.id, fg.name, fg.owner_id
                   FROM family_groups fg
                   JOIN family_members fm ON fm.group_id = fg.id
                   WHERE fm.user_id = ?
                   LIMIT 1""",
                (user_id,),
            ).fetchone()
            if row is None:
                return None
            members = self._load_members(conn, row["id"])
        return {"id": row["id"], "name": row["name"], "owner_id": row["owner_id"], "members": members}

    def create_group(self, owner_id: int, name: str = "Family") -> dict:
        """Create a new family group owned by owner_id."""
        with self._db.connect() as conn:
            existing = conn.execute(
                """SELECT fg.id FROM family_groups fg
                   JOIN family_members fm ON fm.group_id = fg.id
                   WHERE fm.user_id = ?""",
                (owner_id,),
            ).fetchone()
            if existing:
                raise ValueError("You are already in a family group.")
            cur = conn.execute(
                "INSERT INTO family_groups (owner_id, name) VALUES (?,?)", (owner_id, name)
            )
            group_id = cur.lastrowid
            conn.execute(
                "INSERT INTO family_members (group_id, user_id, status) VALUES (?,?,'active')",
                (group_id, owner_id),
            )
            members = self._load_members(conn, group_id)
        return {"id": group_id, "name": name, "owner_id": owner_id, "members": members}

    def invite_by_email(self, owner_id: int, email: str) -> dict:
        """Invite a user (by email) to the owner's family group."""
        email = email.strip().lower()
        with self._db.connect() as conn:
            # Verify caller owns a group
            group_row = conn.execute(
                "SELECT id FROM family_groups WHERE owner_id=?", (owner_id,)
            ).fetchone()
            if group_row is None:
                raise ValueError("You don't own a family group. Create one first.")
            group_id = group_row["id"]

            # Find the invitee
            invitee = conn.execute(
                "SELECT id, username FROM users WHERE lower(email)=?", (email,)
            ).fetchone()
            if invitee is None:
                raise ValueError(f"No user with email '{email}' found.")
            if invitee["id"] == owner_id:
                raise ValueError("You can't invite yourself.")

            # Check if already a member
            existing = conn.execute(
                "SELECT status FROM family_members WHERE group_id=? AND user_id=?",
                (group_id, invitee["id"]),
            ).fetchone()
            if existing:
                raise ValueError(f"{invitee['username']} is already in your family group.")

            conn.execute(
                "INSERT INTO family_members (group_id, user_id, status) VALUES (?,?,'pending')",
                (group_id, invitee["id"]),
            )
        return {"invited": invitee["username"], "email": email, "status": "pending"}

    def accept_invite(self, user_id: int) -> bool:
        """Accept a pending invite for user_id."""
        with self._db.connect() as conn:
            cur = conn.execute(
                """UPDATE family_members SET status='active'
                   WHERE user_id=? AND status='pending'""",
                (user_id,),
            )
        return cur.rowcount > 0

    def leave_group(self, user_id: int) -> bool:
        """Leave or disband the family group."""
        with self._db.connect() as conn:
            # If owner, disband entire group
            group_row = conn.execute(
                "SELECT id FROM family_groups WHERE owner_id=?", (user_id,)
            ).fetchone()
            if group_row:
                conn.execute("DELETE FROM family_groups WHERE id=?", (group_row["id"],))
                return True
            # Otherwise just remove self
            cur = conn.execute(
                """DELETE FROM family_members
                   WHERE user_id=? AND status IN ('active','pending')""",
                (user_id,),
            )
        return cur.rowcount > 0

    def remove_member(self, owner_id: int, target_user_id: int) -> bool:
        if target_user_id == owner_id:
            return False  # use leave_group to disband instead
        with self._db.connect() as conn:
            group_row = conn.execute(
                "SELECT id FROM family_groups WHERE owner_id=?", (owner_id,)
            ).fetchone()
            if group_row is None:
                return False
            cur = conn.execute(
                "DELETE FROM family_members WHERE group_id=? AND user_id=?",
                (group_row["id"], target_user_id),
            )
        return cur.rowcount > 0

    # ── internal ──────────────────────────────────────────────────────────────

    def _load_members(self, conn, group_id: int) -> List[dict]:
        rows = conn.execute(
            """SELECT u.id, u.username, u.email, fm.status
               FROM family_members fm JOIN users u ON fm.user_id = u.id
               WHERE fm.group_id = ?""",
            (group_id,),
        ).fetchall()
        return [{"id": r["id"], "username": r["username"],
                 "email": r["email"], "status": r["status"]} for r in rows]
