import frappe

def save_job_card(doc, method):

    if doc.operation:
        doc.quality_inspection_required = frappe.db.get_value("Operation", doc.operation, "quality_inspection_required")


    if doc.work_order:
        wo = frappe.get_doc("Work Order", doc.work_order)
        for i in wo.budget_bom_reference:
            doc.append("budget_bom_reference",{
                "budget_bom": i.budget_bom
            })