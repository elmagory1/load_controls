import frappe


def validate_mr(doc, method):
    if doc.budget_bom:
        for i in doc.items:
            i.budget_bom_rate = i.rate