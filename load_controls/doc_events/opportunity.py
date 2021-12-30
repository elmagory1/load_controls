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
    print(a)
    print(b)
    print(c)
    print(d)
    print(e)
    print(f)
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
    workstation = frappe.db.get_single_value('Manufacturing Settings', 'default_workstation')
    operation = frappe.db.get_single_value('Manufacturing Settings', 'enclosure_default_operation')
    e_operation = frappe.db.get_single_value('Manufacturing Settings', 'default_operation')
    m_operation = frappe.db.get_single_value('Manufacturing Settings', 'mechanical_bom_default_operation')
    doc = get_mapped_doc("Opportunity", name, {
        "Opportunity": {
            "doctype": "Budget BOM",
            "validation": {
                "status": ["=", "Open"]
            },
            "field_map": {
                "party_name": "customer",
            }
        }
    })
    doc.posting_date = opportunity.expected_closing
    doc.expected_closing_date = opportunity.expected_closing
    for ii in opportunity.items:
        if ii.item_code in selections:
            doc.append("fg_sellable_bom_details", {
                "item_code": ii.item_code,
                "item_name": ii.item_name,
                "qty": ii.qty,
                "uom": ii.uom,
                "workstation": workstation,
                "operation": operation,
                "operation_time_in_minutes": 1,

            })

    for xx in ['electrical_bom_details', 'mechanical_bom_details']:
        doc.append(xx, {
            "qty": 1,
            "workstation": workstation,
            "operation": e_operation if xx == 'electrical_bom_details' else m_operation if xx == 'mechanical_bom_details' else "",
            "operation_time_in_minutes": 1,

        })
    activity_planner = doc.insert()
    return activity_planner.name