import frappe


def validate_mr(doc, method):
    if doc.budget_bom:
        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s""", ('To PO and SO', doc.budget_bom))
        frappe.db.commit()
        for i in doc.items:
            i.budget_bom_rate = i.rate