import frappe

def save_job_card(doc, method):

    if doc.operation:
        doc.quality_inspection_required = frappe.db.get_value("Operation", doc.operation, "quality_inspection_required")