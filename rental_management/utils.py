import frappe

def get_third_party_owner_account(party, company, party_type):
    """Get account for Third Party Owner party type"""
    if party_type == "Third Party Owner":
        try:
            owner = frappe.get_doc("Third Party Owner", party)
            return owner.get_commission_account(company)
        except:
            return None
    return None
