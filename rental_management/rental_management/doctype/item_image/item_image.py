import frappe
from frappe.model.document import Document

class ItemImage(Document):
	def validate(self):
		# Ensure only one primary image per item
		if self.is_primary:
			existing_primary = frappe.db.sql("""
				SELECT name FROM `tabItem Image` 
				WHERE item = %s AND is_primary = 1 AND name != %s
			""", (self.item, self.name or ''))
			
			if existing_primary:
				# Remove primary flag from other images
				frappe.db.sql("""
					UPDATE `tabItem Image` 
					SET is_primary = 0 
					WHERE item = %s AND name != %s
				""", (self.item, self.name or ''))
