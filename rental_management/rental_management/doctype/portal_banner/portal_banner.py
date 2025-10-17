import frappe
from frappe.model.document import Document

class PortalBanner(Document):
	def validate(self):
		# Ensure display order is unique
		if self.display_order:
			existing = frappe.db.get_value(
				"Portal Banner", 
				{"display_order": self.display_order, "name": ["!=", self.name], "is_active": 1},
				"name"
			)
			if existing:
				frappe.throw(f"Display Order {self.display_order} is already used by another active banner")
