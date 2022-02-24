import frappe, json
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.stock_ledger import get_previous_sle


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
    default_warehouse = frappe.db.get_single_value('Manufacturing Settings', 'default_warehouse_for_request_for_quotation')

    bb_doc = get_mapped_doc("Material Request", name, {
        "Material Request": {
            "doctype": "Request for Quotation",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Material Request Item": {
            "doctype": "Request for Quotation Item",
            "field_map": {}
        },
        "Budget BOM Reference": {
            "doctype": "Budget BOM Reference",
            "field_map": {}
        }
    })
    bb_doc.warehoused = default_warehouse if default_warehouse else ""
    for i in bb_doc.items:
        i.warehouse = default_warehouse if default_warehouse else ""
        i.available_qty = get_balance_qty(i.item_code, default_warehouse if default_warehouse else i.warehouse)

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

    if 'item_group' in data:
        final_items = get_item_group_items(data['item_group'], final_items)

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

def get_item_group_items(item_group, items):
    itemss = []
    for i in items:
        if i.item_group == item_group:
            itemss.append(i)
    return itemss


@frappe.whitelist()
def get_mr(mr, item_group, brand, supplier):
    data = json.loads(mr)
    items = []
    bb = []
    suppliers = []
    condition = ""
    default_warehouse = frappe.db.get_single_value('Manufacturing Settings', 'default_warehouse_for_request_for_quotation')

    if item_group:
        condition += " and MRI.item_group='{0}'".format(item_group)
    for x in data:
        bb_references = frappe.db.sql(""" SELECT * FROm `tabBudget BOM References` WHERE parent=%s """, x, as_dict=1)
        for xx in bb_references:
            if xx.budget_bom not in bb:
                bb.append(xx.budget_bom)

        mr = frappe.db.sql(""" SELECT warehouse,item_code, item_name, description, uom,conversion_factor, stock_uom, qty,budget_bom_rate,rate, amount,available_qty, required_qty 
                              FROM `tabMaterial Request Item` MRI WHERE MRI.parent=%s {0}""".format(condition), x,as_dict=1)
        for i in mr:
            i.warehouse = default_warehouse if default_warehouse else ""
            i.available_qty = get_balance_qty(i.item_code, default_warehouse if default_warehouse else i.warehouse )
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

    return items, bb, suppliers, default_warehouse

def existing(items, item):
    for i in items:
        if i.item_code == item.item_code:
            i.qty += item.qty
            i.required_qty = i.qty = i.available_qty
            return True
    return False

def get_balance_qty(item_code, warehouse):
    time = frappe.utils.now_datetime().time()
    date = frappe.utils.now_datetime().date()
    previous_sle = get_previous_sle({
        "item_code": item_code,
        "warehouse": warehouse,
        "posting_date": date,
        "posting_time": time
    })
    balance = previous_sle.get("qty_after_transaction") or 0
    return balance