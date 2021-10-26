import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_bb(source_name, target_doc=None):
    doc = get_mapped_doc("Opportunity", source_name, {
        "Opportunity": {
            "doctype": "Budget BOM",
            "field_map":{
                "party_name": "customer"
            }
        }
    }, ignore_permissions=True)

    return doc