import frappe

def on_save_wo(doc, method):
    doc.additional_operating_cost = 0