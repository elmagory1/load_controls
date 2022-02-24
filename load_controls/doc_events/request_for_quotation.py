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
            if 'supplier' in data and data['supplier'] and item_supplier[0].supplier == data['supplier']:
                bb_doc.append("suppliers", {
                    "supplier": item_supplier[0].supplier
                })
            elif 'supplier' not in data:
                bb_doc.append("suppliers", {
                    "supplier": item_supplier[0].supplier
                })
        else:
            frappe.throw("Please set supplier in item master for item " + str(i.item_code))
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


@frappe.whitelist()
def get_mr(mr, item_group, brand, supplier):
    data = json.loads(mr)
    items = []
    bb = []
    suppliers = []
    condition = ""
    if item_group:
        condition += " and MRI.item_group='{0}'".format(item_group)
    for x in data:
        bb_references = frappe.db.sql(""" SELECT * FROm `tabBudget BOM References` WHERE parent=%s """, x, as_dict=1)
        for xx in bb_references:
            if xx.budget_bom not in bb:
                bb.append(xx.budget_bom)

        mr = frappe.db.sql(""" SELECT item_code, item_name, description, uom,conversion_factor, stock_uom, qty,budget_bom_rate,rate, amount 
                              FROM `tabMaterial Request Item` MRI WHERE MRI.parent=%s {0}""".format(condition), x,as_dict=1)
        for i in mr:
            item = frappe.get_doc("Item", i.item_code)
            if not brand or item.brand == brand:
                if len(item.supplier_items) == 0 and not supplier:
                    if not existing(items, i):
                        items.append(i)
                elif len(item.supplier_items) > 0 and supplier and item.supplier_items[0].supplier == supplier :
                    if item.supplier_items[0].supplier not in suppliers:
                        suppliers.append(item.supplier_items[0].supplier)
                    if not existing(items, i):
                        items.append(i)

                elif len(item.supplier_items) > 0 and not supplier:
                    if item.supplier_items[0].supplier not in suppliers:
                        suppliers.append(item.supplier_items[0].supplier)

                    if not existing(items, i):
                        items.append(i)

    return items, bb, suppliers

def existing(items, item):
    for i in items:
        if i.item_code == item.item_code:
            i.qty += item.qty
            return True
    return False