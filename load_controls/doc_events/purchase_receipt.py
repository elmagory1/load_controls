import frappe, json

def on_submit_pr(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                          ("To Purchase Invoice", i.budget_bom))
            frappe.db.commit()

def on_cancel_pr(doc, method):
    for i in doc.budget_bom_reference:
        if i.budget_bom:
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                          ("To Purchase Receipt", i.budget_bom))
            frappe.db.commit()

def validate_pr(doc, method):
    for i in doc.items:
        if i.purchase_order_item:
            gpd = frappe.db.sql(""" SELECT * FROM `tabGate Pass` GP 
                                       INNER JOIN `tabGate Pass Items` GPI ON GPI.parent = GP.name 
                                       WHERE GPI.purchase_order_detail=%s and GP.docstatus =1 """,
                                i.purchase_order_item, as_dict=1)
            if len(gpd) == 0:
                frappe.throw("Please create Gate Pass from Purchase Order first")



@frappe.whitelist()
def get_receive_qty(items):
    data = json.loads(items)

    for i in data:
        if "purchase_order_item" in i:
            gpd = frappe.db.sql(""" SELECT * FROM `tabGate Pass` GP 
                                    INNER JOIN `tabGate Pass Items` GPI ON GPI.parent = GP.name 
                                    WHERE GPI.purchase_order_detail=%s and GP.docstatus =1 """, i['purchase_order_item'],as_dict=1)


            po = frappe.db.sql(""" SELECT * FROM `tabPurchase Order Item` WHERE name=%s """,
                                i['purchase_order_item'], as_dict=1)
            if len(gpd) == 0:
                frappe.throw("Please create Gate Pass from Purchase Order first")
            i['received_qty'] = gpd[0].received_qty if len(gpd) > 0 else 0
            i['gate_pass_qty'] = gpd[0].qty if len(gpd) > 0 else 0
            i['po_qty'] = po[0].qty if len(po) > 0 else 0

    return data