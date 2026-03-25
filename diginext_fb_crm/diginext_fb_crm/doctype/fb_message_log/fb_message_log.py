import frappe
from frappe.model.document import Document

class FBMessageLog(Document):
    def after_insert(self):
        # Sau khi lưu message mới, tự động tạo CRM Lead nếu được cấu hình
        page_config = frappe.get_doc("FB Page Config", self.page_config)
        if page_config.auto_create_lead and not self.crm_lead:
            self._tao_crm_lead()

    def _tao_crm_lead(self):
        # Kiểm tra Lead đã tồn tại theo sender PSID chưa
        existing_lead = frappe.db.get_value(
            "CRM Lead",
            {"custom_fb_psid": self.sender_psid},
            "name"
        )

        if existing_lead:
            # Lead đã có — chỉ liên kết message log với lead đó
            self.db_set("crm_lead", existing_lead)
        else:
            # Tạo CRM Lead mới
            lead = frappe.get_doc({
                "doctype": "CRM Lead",
                "lead_name": self.sender_name or self.sender_psid,
                "source": "Facebook",
                "custom_fb_psid": self.sender_psid,
                "notes": f"Lead tạo tự động từ Facebook Messenger\nPSID: {self.sender_psid}"
            })
            lead.insert(ignore_permissions=True)
            self.db_set("crm_lead", lead.name)
            frappe.logger().info(f"[FB CRM] Tạo CRM Lead mới: {lead.name} cho PSID {self.sender_psid}")
