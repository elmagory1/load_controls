import frappe,json

@frappe.whitelist()
def submit_q(doc, event):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,("Quotation In Progress", i.budget_bom))
            frappe.db.commit()

    for ii in doc.budget_bom_opportunity:
        frappe.db.sql(""" UPDATE `tabOpportunity` SET status='Quotation' WHERE name=%s  """, (ii.opportunity))
        frappe.db.commit()

@frappe.whitelist()
def cancel_q(doc, event):
    for i in doc.budget_bom_reference:

        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s, quotation_cancelled=1 WHERE name=%s  """,("To Quotation", i.budget_bom))
            frappe.db.commit()

    for ii in doc.budget_bom_opportunity:
        frappe.db.sql(""" UPDATE `tabOpportunity` SET status='Open' WHERE name=%s  """, (ii.opportunity))
        frappe.db.commit()

@frappe.whitelist()
def get_opportunity(doctype,target,e,r,t,filter):

    condition = ""
    if 'party_name' in filter and filter['party_name']:
        print(filter['party_name'])
        party = filter['party_name']
        condition += " and O.party_name = '{0}' ".format(party)

    query = """ SELECT O.name, O.party_name FROM `tabOpportunity` as O INNER JOIN `tabBudget BOM` as BB ON BB.opportunity = O.name  WHERE O.status='Open' and BB.docstatus = 1 {0} GROUP BY O.name """.format(condition)
    opportunities = frappe.db.sql(query,as_dict=1)
    return opportunities

@frappe.whitelist()
def get_updated_costs(budget_boms):
    data = json.loads(budget_boms)
    items = []
    for i in data:
        print("BUDGET BOOOOOOOOOOOOOOOOOOOOOM")
        print(i['budget_bom'])
        bb = frappe.db.sql(""" SELECT BBFD.item_code, BB.total_cost FROM `tabBudget BOM` BB INNER JOIN `tabBudget BOM FG Details` BBFD ON BBFD.parent=BB.name WHERE BB.name=%s """, i['budget_bom'], as_dict=1)
        items.append(bb)
    return items