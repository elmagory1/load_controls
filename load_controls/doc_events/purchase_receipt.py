import frappe

def on_submit_pr(doc, method):
    print(doc.doctype)
    doctype = "Purchase Invoice" if doc.doctype == 'Purchase Receipt' else 'Purchase Receipt'

    po = frappe.db.sql(""" SELECT COUNT(*) as count FROM `tabPurchase Order` Where budget_bom=%s and docstatus=1 """, doc.budget_bom, as_dict=1)
    pi_query = """ SELECT COUNT(*) as count FROM `tab{0}` Where budget_bom='{1}' and docstatus=1""".format(doctype, doc.budget_bom)
    print(pi_query)
    pi = frappe.db.sql(pi_query, as_dict=1)
    print(po)
    print(pi)
    if po[0].count > 0 and pi[0].count > 0:
        update_budget_bom(doc)


def update_budget_bom(doc):
    if doc.budget_bom:
        budget_bom = frappe.db.sql(""" SELECT * FROM `tabBudget BOM` WHERE name=%s""", doc.budget_bom, as_dict=1)
        status = ""
        if budget_bom[0].status == "To PO and SO":
            status = "To SO"

        elif budget_bom[0].status == "To PO":
            status = "Completed"

        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s""",(status, doc.budget_bom))
        frappe.db.commit()