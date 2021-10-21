import frappe


def validate_mr(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s""", ('To PO and SO', i.budget_bom))
            frappe.db.commit()
            for ii in doc.items:
                if ii.budget_bom_raw_material:
                    rate = frappe.db.sql(""" SELECT * from `tabBudget BOM Raw Material` WHERE name=%s""", ii.budget_bom_raw_material, as_dict=1)
                    ii.budget_bom_rate =  ii.rate if rate[0].discount_rate == 0 else rate[0].discount_rate

def cancel_mr(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s""", ('To Material Request', i.budget_bom))
            frappe.db.commit()