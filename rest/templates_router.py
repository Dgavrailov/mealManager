"""REST endpoints for recipe templates — wired into MealRouter."""

from dto.validators import ValidationError, validate_template_payload


class TemplateHandlerMixin:

    def list_templates(self, _q):
        self._send_json(self.template_repo.get_all(user_id=self._effective_uid))

    def create_template(self, _q):
        body   = self._read_json()
        data   = validate_template_payload(body)
        result = self.template_repo.create(data, user_id=self._effective_uid)
        self._send_json(result, 201)

    def get_template(self, _q, tid: str):
        t = self.template_repo.get_by_id(int(tid), user_id=self._effective_uid)
        if t is None:
            self._send_json({"error": "Template not found"}, 404)
        else:
            self._send_json(t)

    def update_template(self, _q, tid: str):
        body   = self._read_json()
        data   = validate_template_payload(body)
        result = self.template_repo.update(int(tid), data, user_id=self._effective_uid)
        if result is None:
            self._send_json({"error": "Template not found"}, 404)
        else:
            self._send_json(result)

    def delete_template(self, _q, tid: str):
        if self.template_repo.delete(int(tid), user_id=self._effective_uid):
            self._send_json({"deleted": int(tid)})
        else:
            self._send_json({"error": "Template not found"}, 404)
