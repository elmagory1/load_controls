import frappe, json
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def get_mr(supplier, mr):
    data = json.loads(mr)
    items = []
    bb = []
    for x in data:
        bb_references = frappe.db.sql(""" SELECT * FROm `tabBudget BOM References` WHERE parent=%s """, x, as_dict=1)
        for xx in bb_references:
            if xx.budget_bom not in bb:
                bb.append(xx.budget_bom)

        mr = frappe.db.sql(""" SELECT item_code, item_name, description, uom,conversion_factor, stock_uom, qty,budget_bom_rate,rate, amount 
                              FROM `tabMaterial Request Item` MRI WHERE MRI.parent=%s """, x,as_dict=1)
        for i in mr:
            item = frappe.get_doc("Item", i.item_code)

            for y in item.supplier_items:
                if y.supplier == supplier and not existing(items, i):
                    items.append(i)
    return items, bb

def existing(items, item):
    for i in items:
        if i.item_code == item.item_code and i.budget_bom_rate == item.budget_bom_rate:
            i.qty += item.qty
            return True
    return False

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
                    "discount": "budget_bom_rate"
                }
            },
            "Budget BOM Raw Material Modifier": {
                "doctype": "Material Request Item",
                "field_map": {
                    "name": "budget_bom_raw_material",
                    "discount": "budget_bom_rate"
                }
            }
        })

        for xx in bb_doc.items:
            items.append(xx)

        items = consolidate_items(items)
        bbs.append({
            "budget_bom": x
        })

    return items, bbs


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


def on_submit_sq(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                          ("To Purchase Order", i.budget_bom))
            frappe.db.commit()

def on_cancel_sq(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                          ("To Supplier Quotation", i.budget_bom))
            frappe.db.commit()
