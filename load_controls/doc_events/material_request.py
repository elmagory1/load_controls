import frappe


@frappe.whitelist()
def get_budget_bom(doctype,target,e,r,t,filter):
    print("FILTEEEEEEEEEEEEEEEER")
    print(filter)
    print(tuple(filter['data']))
    condition = ""
    if len(filter['data']) == 1:
        condition += " and name!='{0}'".format(filter['data'][0])

    if len(filter['data']) > 1:
        condition += " and name not in {0}".format(tuple(filter['data']))

    query = """ SELECT * FROM `tabBudget BOM` WHERE status='To Material Request' and docstatus=1 {0}""".format(condition)
    opportunities = frappe.db.sql(query,as_dict=1)
    return opportunities


def validate_mr(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            for ii in doc.items:
                if ii.budget_bom_raw_material:
                    rate = frappe.db.sql(""" SELECT * from `tabBudget BOM Raw Material` WHERE name=%s""", ii.budget_bom_raw_material, as_dict=1)
                    ii.budget_bom_rate =  ii.rate if rate[0].discount_rate == 0 else rate[0].discount_rate
