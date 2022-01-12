import frappe


@frappe.whitelist()
def get_mr(supplier, mr):

    mr = frappe.db.sql(""" SELECT * FROm `tabMaterial Request Item` MRI WHERE MRI.parent=%s """, (mr),as_dict=1)
    items = []
    for i in mr:
        item = frappe.get_doc("Item", i.item_code)
        for x in item.supplier_items:
            if x.supplier == supplier:
                i.docstatus = 0
                items.append(i)
    return items
