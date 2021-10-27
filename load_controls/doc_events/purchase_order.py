import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def generate_gate_pass(source_name, target_doc=None):
    print("==================================================")
    doc = get_mapped_doc("Purchase Order", source_name, {
        "Purchase Order": {
            "doctype": "Gate Pass",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Purchase Order Item": {
            "doctype": "Gate Pass Items",
        }

    }, target_doc)

    return doc

@frappe.whitelist()
def check_gate_pass(name):
    gate_pass = frappe.db.sql(""" SELECT COUNT(*) as count FROM `tabGate Pass` WHERE purchase_order=%s and docstatus < 2 """, name,as_dict=1)

    return gate_pass[0].count > 0
