import frappe,json

def validate_q(doc, method):
    sum = 0
    for i in doc.budget_bom_reference:
        total = frappe.db.get_value("Budget BOM", i.budget_bom,"total_additional_operation_cost")
        sum += total
    doc.additional_operating_cost = sum

@frappe.whitelist()
def check_bb_status(bb):
    data = json.loads(bb)
    for i in data:
        bbb = frappe.db.sql(""" SELECT * FROM `tabBudget BOM` WHERE name=%s""", i['budget_bom'], as_dict=1)
        if "Sales Order" in bbb[0].status:
            return True
    return False

@frappe.whitelist()
def po_received(name,amended_from):
    frappe.db.sql(""" UPDATE `tabQuotation` SET status='Open' WHERE name=%s """, name)
    frappe.db.commit()
    quotation = frappe.get_doc("Quotation", name)
    for i in quotation.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s, submitted_changes=0 WHERE name=%s  """,
                          ("To Design", i.budget_bom))
            frappe.db.commit()

@frappe.whitelist()
def revise_the_quote(name):
    quotation = frappe.get_doc("Quotation", name)
    quotation.cancel()

@frappe.whitelist()
def submit_quotation(name):
    frappe.db.sql(""" UPDATE `tabQuotation` SET status='In Progress' WHERE name=%s """, name)
    frappe.db.commit()
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

    query = """ SELECT O.name, O.party_name FROM `tabOpportunity` as O 
  INNER JOIN `tabBudget BOM` as BB ON BB.opportunity = O.name  WHERE O.status='Qualified' and BB.docstatus = 1 {0} GROUP BY O.name """.format(condition)
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