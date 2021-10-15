import frappe

@frappe.whitelist()
def submit_q(doc, event):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,("To Design", i.budget_bom))
            frappe.db.commit()

@frappe.whitelist()
def cancel_q(doc, event):
    for i in doc.budget_bom_reference:

        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s, quotation_amended=1 WHERE name=%s  """,("To Quotation", i.budget_bom))
            frappe.db.commit()