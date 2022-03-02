import frappe

def on_submit_se(doc, method):
    if doc.stock_entry_type == 'Manufacture' and doc.work_order:
        wo = frappe.get_doc("Work Order", doc.work_order)

        for i in wo.budget_bom_reference:
            if i.budget_bom:
                frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s  """,
                              ("To Deliver", i.budget_bom))
                frappe.db.commit()

    if doc.stock_entry_type == 'Material Transfer for Manufacture' and doc.work_order:
        frappe.db.sql(""" UPDATE `tabWork Order` SET material_transferred_for_manufacturing=1 WHERE name=%s  """,doc.work_order)
        frappe.db.commit()

def on_save_se(doc, method):
    print("DOOOOOOOOOOOOOOOOOOC")
    print(doc.__dict__)
    if doc.stock_entry_type == 'Manufacture' and doc.work_order and doc.flags.in_insert:
        wo = frappe.get_doc("Work Order", doc.work_order)
        for i in wo.budget_bom_reference:
            if i.budget_bom:
                bb = frappe.get_doc("Budget BOM", i.budget_bom)
                for xxx in bb.additional_operation_cost:
                    doc.append("additional_costs",{
                        "expense_account": xxx.cost_type,
                        "description": xxx.description,
                        "amount": xxx.amount,
                    })
        total_amount = 0
        for i in doc.additional_costs:
            total_amount += i.amount
        doc.total_additional_costs = total_amount
        doc.value_difference = total_amount

def check_costs(xxx, additional_costs):
    for i in additional_costs:
        if i.expense_account == xxx.cost_type:
            i.amount += xxx.amount
            return True
    return False