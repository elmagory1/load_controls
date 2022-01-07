import frappe, json

def on_submit_so(doc, method):
    if not doc.cost_center:
        frappe.throw("Please Generate Project Code First")
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
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,("To Sales Order", i.budget_bom))
            frappe.db.commit()

@frappe.whitelist()
def generate_cost_centers(items, name, customer,project_code, company):
    items_data = json.loads(items)

    company = frappe.get_doc("Company", company)
    default_project_code = frappe.db.get_single_value('Global Defaults', 'default_project_code')
    if not default_project_code:
        frappe.throw("Please Set Default Project Code in Global Defaults")
    generate_cc(project_code, customer, name, company, items_data,default_project_code)

def generate_cc(project_code, customer, name, company, items_data,default_project_code):
    cc_name = ""
    if not project_code:
        args = {
            "doctype": "Cost Center",
            "cost_center_name": name,
            "is_group": 1,
            "parent_cost_center": default_project_code,
            "sales_order": name,
            'is_root': 'true'
        }
        cc = frappe.new_doc("Cost Center")
        cc.update(args)
        cc.old_parent = ""
        cc.insert()
        cc_name = cc.name

        frappe.db.sql(""" UPDATE `tabSales Order` SET cost_center=%s WHERE name=%s""", (cc_name, name))
        frappe.db.commit()
    else:
        cc_name = name + " - " + company.abbr

    for i in items_data:
        if 'project_code' not in i:
            obj = {
                "doctype": "Cost Center",
                "cost_center_name": name + "-" + i['item_code'],
                "parent_cost_center": cc_name,
                "sales_order": name
            }
            ccc = frappe.get_doc(obj).insert()
            frappe.db.sql(""" UPDATE `tabSales Order Item` SET project_code=%s WHERE name=%s""", (ccc.name, i['name']))
            frappe.db.commit()