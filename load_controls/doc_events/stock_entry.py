import frappe

def on_submit_se(doc, method):
    if doc.stock_entry_type == 'Manufacture' and doc.work_order:
        wo = frappe.get_doc("Work Order", doc.work_order)

        for i in wo.budget_bom_reference:
            if i.budget_bom:
                frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                              ("To Deliver", i.budget_bom))
                frappe.db.commit()


def on_save_se(doc, method):
    if doc.stock_entry_type == 'Manufacture' and doc.work_order:
        wo = frappe.get_doc("Work Order", doc.work_order)
        for i in wo.budget_bom_reference:
            if i.budget_bom:
                bb = frappe.get_doc("Budget BOM", i.budget_bom)
                for xxx in bb.additional_operation_cost:
                    if not check_costs(xxx, doc.additional_costs):
                        doc.append("additional_costs",{
                            "expense_account": xxx.cost_type,
                            "description": xxx.description,
                            "amount": xxx.amount,
                        })


def check_costs(xxx, additional_costs):
    for i in additional_costs:
        if i.expense_account == xxx.cost_type:
            i.amount += xxx.amount
            return True
    return False