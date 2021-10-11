import frappe

@frappe.whitelist()
def submit_q(doc, event):
    if doc.budget_bom:
        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,("To Design", doc.budget_bom))
        frappe.db.commit()

@frappe.whitelist()
def cancel_q(doc, event):
    if doc.budget_bom:
        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s, quotation_amended=1 WHERE name=%s  """,("To Quotation", doc.budget_bom))
        frappe.db.commit()