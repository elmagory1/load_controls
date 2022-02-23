import frappe, json
from frappe.model.mapper import get_mapped_doc


def on_submit_rfq(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                          ("To Supplier Quotation", i.budget_bom))
            frappe.db.commit()

def on_cancel_rfq(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                          ("To Request for Quotation", i.budget_bom))
            frappe.db.commit()


@frappe.whitelist()
def generate_rfq(name, values):
    data = json.loads(values)
    filters = {}
    if 'item_group' in data:
        filters['item_group'] = ["=", data['item_group']]
    bb_doc = get_mapped_doc("Material Request", name, {
        "Material Request": {
            "doctype": "Request for Quotation",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Material Request Item": {
            "doctype": "Request for Quotation Item",
            "field_map": {},
            "validation": filters
        },
        "Budget BOM Reference": {
            "doctype": "Budget BOM Reference",
            "field_map": {}
        }
    })
    for i in bb_doc.items:
        item_supplier = frappe.db.sql("""  SELECT * FROm `tabItem Supplier` WHERE parent=%s LIMIT 1""", i.item_code,as_dict=1)
        if len(item_supplier) > 0:

            bb_doc.append("suppliers", {
                "supplier": item_supplier[0].supplier
            })
        else:
            frappe.throw("Please set supplier in item master")
    bb_doc.message_for_supplier = "Message for supplier here"
    final_items = bb_doc.items

    if 'brand' in data:
        final_items = get_brand_items(data['brand'], bb_doc.items)

    bb_doc.items = final_items
    if len(bb_doc.items) == 0 :
        frappe.throw("No Items added")
    rqs = frappe.get_doc(bb_doc).insert()
    return rqs.name


def get_brand_items(brand, items):
    itemss = []
    for i in items:
        item_master = frappe.get_doc("Item", i.item_code)
        if item_master == brand:
            itemss.append(i)
    return itemss