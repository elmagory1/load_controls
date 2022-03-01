import frappe


def on_submit_pl(doc, method):
    if doc.work_order:
        wo = frappe.get_doc("Work Order", doc.work_order)
        for i in doc.locations:
            woi = frappe.db.sql(""" SELECT * FROm `tabWork Order Item` WHERE name=%s""", i.work_order_item, as_dict=1)
            if len(woi) > 0:
                frappe.db.sql(""" UPDATE `tabWork Order Item` SET picked_qty=%s WHERE name=%s """,(woi[0].picked_qty + i.qty,i.work_order_item))
                frappe.db.sql(""" UPDATE `tabWork Order` SET material_transferred_for_manufacturing=%s WHERE name=%s """,(wo.material_transferred_for_manufacturing + 1,doc.work_order))
                frappe.db.commit()