import frappe


def on_submit_pl(doc, method):
    for i in doc.locations:
        woi = frappe.db.sql(""" SELECT * FROm `tabWork Order Item` WHERE name=%s""", i.work_order_item, as_dict=1)
        if len(woi) > 0:
            frappe.db.sql(""" UPDATE `tabWork Order Item` SET picked_qty=%s WHERE name=%s """,(woi[0].picked_qty + i.qty,i.work_order_item))
            frappe.db.commit()