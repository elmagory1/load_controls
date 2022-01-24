import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_bb(source_name, target_doc=None):
    doc = get_mapped_doc("Opportunity", source_name, {
        "Opportunity": {
            "doctype": "Budget BOM",
            "field_map":{
                "party_name": "customer"
            }
        }
    }, ignore_permissions=True)

    return doc


@frappe.whitelist()
@frappe.whitelist()
def get_items(a,b,c,d,e,f):
    activity_types = []
    data = frappe.db.sql(""" SELECT item_code as name, item_name FROM `tabOpportunity Item` WHERE parent=%s""", f['parent'],as_dict=1)
    for i in data:
        activity_planner = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabBudget BOM` AP INNER JOIN `tabBudget BOM FG Details` AB ON AP.name = AB.parent 
                WHERE AP.opportunity=%s and AB.parentfield='fg_sellable_bom_details' and AB.parenttype='Budget BOM' and AB.item_code=%s and AP.docstatus < 2""",
            (f['parent'],i.name),as_dict=1)
        if activity_planner[0].count == 0:
            activity_types.append(i)
    return activity_types


@frappe.whitelist()
def generate_budget_bom(selections, name):
    opportunity = frappe.get_doc("Opportunity", name)
    e_workstation = frappe.db.get_single_value('Manufacturing Settings', 'default_workstation')
    m_workstation = frappe.db.get_single_value('Manufacturing Settings', 'mechanical_bom_default_workstation')
    fg_workstation = frappe.db.get_single_value('Manufacturing Settings', 'encluser_default_workstation')

    operation = frappe.db.get_single_value('Manufacturing Settings', 'enclosure_default_operation')
    e_operation = frappe.db.get_single_value('Manufacturing Settings', 'default_operation')
    m_operation = frappe.db.get_single_value('Manufacturing Settings', 'mechanical_bom_default_operation')

    operation_time_in_minutes = frappe.db.get_single_value('Manufacturing Settings', 'enclosure_time_in_minute')
    e_operation_time_in_minutes = frappe.db.get_single_value('Manufacturing Settings', 'electrical_operation_time_in_minute')
    m_operation_time_in_minutes = frappe.db.get_single_value('Manufacturing Settings', 'mechanical_operation_time_in_minute')
    if not operation:
        frappe.throw("Please Set Enclosure Default Operation in Manufacturing Settings")

    if not e_operation:
        frappe.throw("Please Set Electrical Default Operation in Manufacturing Settings")

    if not m_operation:
        frappe.throw("Please Set Mechanical Default Operation in Manufacturing Settings")

    if not e_workstation:
        e_workstation = frappe.db.get_value("Operation", e_operation, "workstation")
        if not e_workstation:
            frappe.throw("Please Set Either Default Workstation in Operation or Default Electrical Workstation in Manufacturing Settings")

    if not m_workstation:
        m_workstation = frappe.db.get_value("Operation", m_workstation, "workstation")
        if not m_workstation:
            frappe.throw("Please Set Either Default Workstation in Operation or Default Mechanical Workstation in Manufacturing Settings")

    if not fg_workstation:
        fg_workstation = frappe.db.get_value("Operation", fg_workstation, "workstation")
        if not fg_workstation:
            frappe.throw("Please Set Either Default Workstation in Operation or Default Enclosure Workstation in Manufacturing Settings")

    doc = get_mapped_doc("Opportunity", name, {
        "Opportunity": {
            "doctype": "Budget BOM",
            "validation": {
                "status": ["in", ["Open", "Qualified"]]
            },
            "field_map": {
                "party_name": "customer",
            }
        }
    })

    doc.posting_date = opportunity.expected_closing
    doc.expected_closing_date = opportunity.expected_closing
    estimated_bom_operation_cost = 0

    for ii in opportunity.items:
        if ii.item_code in selections:
            hour_rate = frappe.db.get_value("Workstation", fg_workstation, "hour_rate")
            estimated_bom_operation_cost += hour_rate
            doc.append("fg_sellable_bom_details", {
                "item_code": ii.item_code,
                "item_name": ii.item_name,
                "qty": ii.qty,
                "uom": ii.uom,
                "workstation": fg_workstation,
                "operation": operation,
                "operation_time_in_minutes": operation_time_in_minutes ,
                "net_hour_rate": hour_rate ,

            })
    for xx in ['electrical_bom_details', 'mechanical_bom_details']:
        e_hour_rate = frappe.db.get_value("Workstation", e_workstation, "hour_rate")
        m_hour_rate = frappe.db.get_value("Workstation", m_workstation, "hour_rate")
        estimated_bom_operation_cost += (e_hour_rate if xx == 'electrical_bom_details' else m_hour_rate)

        doc.append(xx, {
            "qty": 1,
            "workstation": e_workstation if xx == 'electrical_bom_details' else m_workstation,
            "net_hour_rate": e_hour_rate if xx == 'electrical_bom_details' else m_hour_rate,
            "operation": e_operation if xx == 'electrical_bom_details' else m_operation if xx == 'mechanical_bom_details' else "",
            "operation_time_in_minutes": e_operation_time_in_minutes if xx == 'electrical_bom_details' else m_operation_time_in_minutes,
        })
    doc.estimated_bom_operation_cost = estimated_bom_operation_cost
    doc.operation_cost = estimated_bom_operation_cost
    doc.total_operation_cost = estimated_bom_operation_cost
    doc.total_cost = estimated_bom_operation_cost
    activity_planner = doc.insert()
    return activity_planner.name