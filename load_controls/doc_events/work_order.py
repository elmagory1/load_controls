import frappe, json
from frappe.utils import (
	cint,
	date_diff,
	flt,
	get_datetime,
	get_link_to_form,
	getdate,
	nowdate,
	time_diff_in_hours,
)
from frappe.model.mapper import get_mapped_doc
def on_save_wo(doc, method):
    doc.additional_operating_cost = 0



@frappe.whitelist()
def create_pick_list(source_name, target_doc=None, for_qty=None):
    for_qty = for_qty or json.loads(target_doc).get('for_qty')
    max_finished_goods_qty = frappe.db.get_value('Work Order', source_name, 'qty')
    def update_item_quantity(source, target, source_parent):
        pending_to_issue = flt(source.required_qty) - flt(source.picked_qty)
        desire_to_transfer = flt(source.required_qty) / max_finished_goods_qty * flt(for_qty)

        qty = 0
        if desire_to_transfer <= pending_to_issue:
            qty = desire_to_transfer
        elif pending_to_issue > 0:
            qty = pending_to_issue

        if qty:
            target.qty = qty
            target.stock_qty = qty
            target.uom = frappe.get_value('Item', source.item_code, 'stock_uom')
            target.stock_uom = target.uom
            target.conversion_factor = 1
        else:
            target.delete()

    doc = get_mapped_doc('Work Order', source_name, {
        'Work Order': {
            'doctype': 'Pick List',
            'validation': {
                'docstatus': ['=', 1]
            }
        },
        'Work Order Item': {
            'doctype': 'Pick List Item',
            'postprocess': update_item_quantity,
            'condition': lambda doc: doc.picked_qty < doc.required_qty,
            'field_map': {
                'name': "work_order_item"
            }
        },
    }, target_doc)

    doc.for_qty = for_qty

    doc.set_item_locations()

    return doc