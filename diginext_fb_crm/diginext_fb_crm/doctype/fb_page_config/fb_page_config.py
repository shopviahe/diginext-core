import frappe
from frappe.model.document import Document

class FBPageConfig(Document):
    def validate(self):
        # Kiểm tra không được có 2 config cùng Page ID
        existing = frappe.db.get_value(
            "FB Page Config",
            {"page_id": self.page_id, "name": ("!=", self.name)},
            "name"
        )
        if existing:
            frappe.throw(f"Page ID {self.page_id} đã được cấu hình trong {existing}")

    def before_save(self):
        # Nếu set is_active = 1, tắt các config khác cùng page_id
        if self.is_active:
            frappe.db.set_value(
                "FB Page Config",
                {"page_id": self.page_id, "name": ("!=", self.name)},
                "is_active", 0
            )
