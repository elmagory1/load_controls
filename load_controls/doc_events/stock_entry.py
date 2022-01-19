import frappe

def on_submit_se(doc, method):
    if doc.stock_entry_type == 'Manufacture' and doc.work_order:
        wo = frappe.get_doc("Work Order", doc.work_order)

        for i in wo.budget_bom_reference:
            if i.budget_bom:
                frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                              ("To Deliver", i.budget_bom))
                frappe.db.commit()