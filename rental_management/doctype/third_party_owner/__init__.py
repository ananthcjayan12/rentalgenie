# Copyright (c) 2024, Rental Management and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ThirdPartyOwner(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address_line_1: DF.Data | None
		address_line_2: DF.Data | None
		bank_account_name: DF.Data | None
		bank_account_number: DF.Data | None
		bank_name: DF.Data | None
		city: DF.Data | None
		default_commission_rate: DF.Percent | None
		disabled: DF.Check
		email: DF.Data | None
		ifsc_code: DF.Data | None
		owner_code: DF.Data | None
		owner_name: DF.Data
		phone: DF.Data | None
		pincode: DF.Data | None
		state: DF.Data | None
	# end: auto-generated types

	pass
