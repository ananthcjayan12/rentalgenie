import frappe
from frappe.model.document import Document

class ItemImage(Document):
	def validate(self):
		# If used as child table inside Item, set item link automatically from parent
		if not self.item and getattr(self, 'parenttype', None) == 'Item' and getattr(self, 'parent', None):
			self.item = self.parent

		# Ensure only one primary image per item
		if self.is_primary and self.item:
			existing_primary = frappe.db.sql("""
				SELECT name FROM `tabItem Image` 
				WHERE item = %s AND is_primary = 1 AND name != %s
			""", (self.item, self.name or ''))
			if existing_primary:
				frappe.db.sql("""
					UPDATE `tabItem Image` 
					SET is_primary = 0 
					WHERE item = %s AND name != %s
				""", (self.item, self.name or ''))
