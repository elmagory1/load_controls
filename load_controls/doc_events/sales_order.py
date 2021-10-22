import frappe

def on_submit_so(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """, ("To Design", i.budget_bom))
            frappe.db.commit()


def on_submit_dn(doc, method):
    doctype = "Delivery Note" if doc.doctype == 'Sales Invoice' else doc.doctype
    for i in doc.budget_bom_reference:

        po = frappe.db.sql(""" SELECT COUNT(*) as count FROM `tabSales Order` DD INNER JOIN  `tabBudget BOM References` BBR ON BBR.parent = DD.name and BBR.budget_bom = %s and DD.docstatus=1 """, i.budget_bom, as_dict=1)
        pi_query = """ SELECT COUNT(*) as count FROM `tab{0}` DD INNER JOIN  `tabBudget BOM References` BBR ON BBR.parent = DD.name and BBR.budget_bom = '{1}' and DD.docstatus=1""".format(doctype, i.budget_bom)
        pi = frappe.db.sql(pi_query, as_dict=1)

        if po[0].count > 0 and pi[0].count > 0:
            update_budget_bom(i)

def update_budget_bom(i):
    if i.budget_bom:
        budget_bom = frappe.db.sql(""" SELECT * FROM `tabBudget BOM` WHERE name=%s""", i.budget_bom, as_dict=1)
        status = ""
        if budget_bom[0].status == "To PO and SO":
            status = "To SO"

        elif budget_bom[0].status == "To PO":
            status = "Completed"

        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s""",(status, i.budget_bom))
        frappe.db.commit()

def on_cancel_so(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,("Quotation In Progress", i.budget_bom))
            frappe.db.commit()