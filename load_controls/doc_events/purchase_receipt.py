import frappe

def on_submit_pr(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                          ("To Purchase Invoice", i.budget_bom))
            frappe.db.commit()

def on_cancel_pr(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                          ("To Purchase Receipt", i.budget_bom))
            frappe.db.commit()
