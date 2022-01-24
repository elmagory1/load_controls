import frappe, json
from frappe.model.mapper import get_mapped_doc


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

    query = """ SELECT * FROM `tabBudget BOM` WHERE status='To Material Request and To Work Order' and docstatus=1 {0}""".format(condition)
    opportunities = frappe.db.sql(query,as_dict=1)
    return opportunities


def validate_mr(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            for ii in doc.items:
                if ii.budget_bom_raw_material:
                    rate = frappe.db.sql(""" SELECT * from `tabBudget BOM Raw Material` WHERE name=%s""", ii.budget_bom_raw_material, as_dict=1)
                    rate2 = frappe.db.sql(""" SELECT * from `tabBudget BOM Enclosure Raw Material` WHERE name=%s""", ii.budget_bom_raw_material, as_dict=1)
                    rate1 = frappe.db.sql(""" SELECT * from `tabBudget BOM Raw Material Modifier` WHERE name=%s""", ii.budget_bom_raw_material, as_dict=1)
                    ii.budget_bom_rate =  ii.rate if len(rate) > 0 and rate[0].discount_rate == 0  else rate[0].discount_rate if len(rate) > 0 and rate[0].discount_rate > 0 else 0
                    if len(rate1) > 0:
                        ii.budget_bom_rate = ii.rate if len(rate1) > 0 and rate1[0].discount_rate == 0  else rate1[
                            0].discount_rate if len(rate1) > 0 and rate1[0].discount_rate > 0 else 0
                    if len(rate2) > 0:
                        ii.budget_bom_rate = ii.rate if len(rate2) > 0 and rate2[0].discount_rate == 0  else rate2[
                            0].discount_rate if len(rate2) > 0 and rate2[0].discount_rate > 0 else 0


@frappe.whitelist()
def get_bb(mr):
    data = json.loads(mr)
    items = []
    bbs = []
    for x in data:
        bb_doc = get_mapped_doc("Budget BOM", x, {
            "Budget BOM": {
                "doctype": "Material Request",
                "validation": {
                    "docstatus": ["=", 1]
                }
            },
            "Budget BOM Raw Material": {
                "doctype": "Material Request Item",
                "field_map": {
                    "name": "budget_bom_raw_material"
                }
            },
            "Budget BOM Enclosure Raw Material": {
                "doctype": "Material Request Item",
                "field_map": {
                    "name": "budget_bom_raw_material",
                    "discount_rate": "budget_bom_rate"
                }
            },
            "Budget BOM Raw Material Modifier": {
                "doctype": "Material Request Item",
                "field_map": {
                    "name": "budget_bom_raw_material",
                    "discount_rate": "budget_bom_rate"
                }
            }
        })
        bb_document = frappe.get_doc("Budget BOM", x)
        so = frappe.db.sql(""" SELECT SOI.*, SO.transaction_date FROM `tabSales Order` SO 
                              INNER JOIN `tabSales Order Item` SOI ON SOI.parent = SO.name 
                              INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = SO.name  
                              WHERE BBR.budget_bom = %s
                              """,x,as_dict=1)

        qty = check_qty(bb_document.fg_sellable_bom_details[0].item_code, so)

        for xx in bb_doc.items:
            xx.qty = xx.qty * qty
            xx.schedule_date = bb_doc.posting_date

            items.append(xx)

        items = consolidate_items(items)
        bbs.append({
            "budget_bom": x
        })

    return items, bbs

def check_qty(item_code, items):
    for i in items:
        if i.item_code == item_code:
            return i.qty
    return 1
def consolidate_items(items):
    c_items = []
    for i in items:
        add = False
        for x in c_items:
            if i.item_code == x.item_code and i.budget_bom_rate == x.budget_bom_rate:
                if 'type' in i.__dict__ and i.type:
                    if i.type == 'Deletion':
                        x.qty -= i.qty
                    else:
                        x.qty += i.qty
                else:
                    x.qty += i.qty
                add = True
        if not add:
            c_items.append(i)

    return c_items
