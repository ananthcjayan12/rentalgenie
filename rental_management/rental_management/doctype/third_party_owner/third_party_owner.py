# Copyright (c) 2024, Rental Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ThirdPartyOwner(Document):
	def before_save(self):
		"""Generate owner code before saving"""
		if not self.owner_code:
			self.generate_owner_code()
	
	def generate_owner_code(self):
		"""Generate unique owner code based on owner name"""
		if not self.owner_name:
			return
		
		# Simple code generation - first 3 chars + sequence number
		name_prefix = self.owner_name[:3].upper().replace(" ", "")
		base_code = f"OWN-{name_prefix}"
		
		# Find next available number
		counter = 1
		owner_code = f"{base_code}-{counter:03d}"
		while frappe.db.exists("Third Party Owner", {"owner_code": owner_code, "name": ("!=", self.name)}):
			counter += 1
			owner_code = f"{base_code}-{counter:03d}"
		
		self.owner_code = owner_code
	
	def after_insert(self):
		"""Create commission payable account after inserting owner"""
		self.create_commission_account()
	
	def create_commission_account(self):
		"""Create a dedicated commission payable account for this owner"""
		company = frappe.defaults.get_global_default("company")
		if not company:
			company = frappe.db.get_single_value("Global Defaults", "default_company")
		if not company:
			companies = frappe.get_all("Company", limit=1)
			if companies:
				company = companies[0].name
		
		if not company:
			print("No company found for commission account creation")
			return
		
		company_abbr = frappe.get_cached_value("Company", company, "abbr")
		account_name = f"Commission Payable - {self.owner_name} - {company_abbr}"
		
		# Check if account already exists
		if frappe.db.exists("Account", account_name):
			self.commission_account = account_name
			self.save()
			return account_name
		
		# Find parent account (Current Liabilities for Third Party Owner accounts)
		parent_account = f"Current Liabilities - {company_abbr}"
		if not frappe.db.exists("Account", parent_account):
			# Try to find any Current Liabilities group account
			parent_accounts = frappe.get_all("Account", 
				filters={
					"company": company,
					"is_group": 1,
					"root_type": "Liability"
				}, limit=1)
			if parent_accounts:
				parent_account = parent_accounts[0].name
			else:
				# Fallback: try to find any group account under Liabilities
				parent_accounts = frappe.get_all("Account",
					filters={
						"company": company,
						"is_group": 1,
						"account_name": ["like", "%Liabilit%"]
					}, limit=1)
				if parent_accounts:
					parent_account = parent_accounts[0].name
				else:
					print("No suitable parent account found for commission account")
					return
		
		try:
			# Create commission account with Payable account type (valid ERPNext account type)
			account = frappe.get_doc({
				"doctype": "Account",
				"account_name": f"Commission Payable - {self.owner_name}",
				"parent_account": parent_account,
				"company": company,
				"account_type": "Payable",
				"is_group": 0
			})
			account.insert(ignore_permissions=True)
			
			# Update the commission account field
			self.commission_account = account.name
			self.save()
			
			return account.name
			
		except Exception as e:
			print(f"Error creating commission account: {str(e)}")
			return None
	
	def get_commission_account(self, company=None):
		"""Get or create the commission payable account for this owner"""
		if self.commission_account and frappe.db.exists("Account", self.commission_account):
			return self.commission_account
		
		# If no account exists, create it
		return self.create_commission_account()

@frappe.whitelist()
def create_third_party_owner_from_supplier(supplier_name):
	"""Auto-create Third Party Owner from Supplier"""
	if frappe.db.exists("Third Party Owner", {"supplier_link": supplier_name}):
		# Owner already exists for this supplier
		return frappe.get_value("Third Party Owner", {"supplier_link": supplier_name}, "name")
	
	# Get supplier details
	supplier = frappe.get_doc("Supplier", supplier_name)
	
	# Create new Third Party Owner
	owner = frappe.get_doc({
		"doctype": "Third Party Owner",
		"owner_name": supplier.supplier_name,
		"supplier_link": supplier_name,
		"email": getattr(supplier, 'email_id', ''),
		"phone": getattr(supplier, 'mobile_no', ''),
		"default_commission_rate": 10.0  # Default 10% commission
	})
	
	# Copy address if available
	addresses = frappe.get_all("Dynamic Link", 
		filters={"link_doctype": "Supplier", "link_name": supplier_name, "parenttype": "Address"},
		fields=["parent"]
	)
	
	if addresses:
		address = frappe.get_doc("Address", addresses[0].parent)
		owner.address_line_1 = address.address_line1 or ''
		owner.address_line_2 = address.address_line2 or ''
		owner.city = address.city or ''
		owner.state = address.state or ''
		owner.pincode = address.pincode or ''
	
	owner.insert(ignore_permissions=True)
	
	return owner.name

@frappe.whitelist()
def get_owner_commission_account(owner_name, company=None):
	"""Get commission account for an owner"""
	try:
		owner = frappe.get_doc("Third Party Owner", owner_name)
		return owner.get_commission_account(company)
	except Exception as e:
		frappe.log_error(f"Error getting commission account for owner {owner_name}: {str(e)}")
		return None
