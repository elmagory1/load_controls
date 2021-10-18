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

@frappe.whitelist()
def on_submit_po(doc, method):
    if check_items(doc) and not doc.approve_po_rate:
        frappe.throw("PO Rate not Approved")


def check_items(doc):
    for i in doc.items:
        if i.rate > i.budget_bom_rate:
            return True

    return "Approved"