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
from six import iteritems, itervalues, string_types

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
def consolidate(picked_items, company,stock_entry,pro_doc):

    item_dict = {}
    stock_entry.set('items', [])
    stock_entry.validate_work_order()

    if not stock_entry.posting_date or not stock_entry.posting_time:
        frappe.throw(_("Posting date and posting time is mandatory"))

    stock_entry.set_work_order_details()
    stock_entry.flags.backflush_based_on = frappe.db.get_single_value("Manufacturing Settings",
                                                               "backflush_raw_materials_based_on")

    for item in picked_items:
        item_code = item.alternative_item if item.alternative_item else item.item_code
        item.item_code = item_code
        if item.item_code in item_dict:
            item_dict[item_code]["qty"] += flt(item.qty)
        else:
            item_dict[item_code] = item
    print("==============================================")
    print("Item Diiiiiiiict")
    print(item_dict)
    for item, item_details in item_dict.items():
        for d in [["Account", "expense_account", "stock_adjustment_account"],
                  ["Cost Center", "cost_center", "cost_center"], ["Warehouse", "default_warehouse", ""]]:
            company_in_record = frappe.db.get_value(d[0], item_details.get(d[1]), "company")
            if not item_details.get(d[1]) or (company_in_record and company != company_in_record):
                item_dict[item][d[1]] = frappe.get_cached_value('Company', company, d[2]) if d[2] else None

    if stock_entry.purchase_order and stock_entry.purpose == "Send to Subcontractor":
        # Get PO Supplied Items Details
        item_wh = frappe._dict(frappe.db.sql("""
    							SELECT
    								rm_item_code, reserve_warehouse
    							FROM
    								`tabPurchase Order` po, `tabPurchase Order Item Supplied` poitemsup
    							WHERE
    								po.name = poitemsup.parent and po.name = %s """, stock_entry.purchase_order))

    for item in itervalues(item_dict):
        if stock_entry.pro_doc and cint(stock_entry.pro_doc.from_wip_warehouse):
            item["from_warehouse"] = stock_entry.pro_doc.wip_warehouse
        # Get Reserve Warehouse from PO
        if stock_entry.purchase_order and stock_entry.purpose == "Send to Subcontractor":
            item["from_warehouse"] = item_wh.get(item.item_code)
        item["to_warehouse"] = stock_entry.to_warehouse if stock_entry.purpose == "Send to Subcontractor" else ""

    stock_entry.add_to_stock_entry_detail(item_dict)

    # add finished goods item
    if stock_entry.purpose in ("Manufacture", "Repack"):
        stock_entry.load_items_from_bom()
    stock_entry.set_scrap_items()
    stock_entry.set_actual_qty()
    stock_entry.update_items_for_process_loss()
    stock_entry.validate_customer_provided_item()
    stock_entry.calculate_rate_and_amount()
def get_bom_raw_materials(work_order, company,stock_entry,pro_doc):

    items = frappe.db.sql(""" SELECT PLI.* FROM `tabPick List` PL 
                      INNER JOIN `tabPick List Item` PLI ON PLI.parent = PL.name 
                      WHERE PL.work_order=%s and PL.docstatus=1""", work_order,as_dict=1)

    consolidate(items, company,stock_entry,pro_doc)
@frappe.whitelist()
def make_stock_entry(work_order_id, purpose, company, qty=None):
    work_order = frappe.get_doc("Work Order", work_order_id)
    if not frappe.db.get_value("Warehouse", work_order.wip_warehouse, "is_group"):
        wip_warehouse = work_order.wip_warehouse
    else:
        wip_warehouse = None

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.purpose = purpose
    stock_entry.work_order = work_order_id
    stock_entry.company = work_order.company
    stock_entry.from_bom = 1
    stock_entry.bom_no = work_order.bom_no
    stock_entry.use_multi_level_bom = work_order.use_multi_level_bom
    stock_entry.fg_completed_qty = qty or (flt(work_order.qty) - flt(work_order.produced_qty))
    if work_order.bom_no:
        stock_entry.inspection_required = frappe.db.get_value('BOM',
            work_order.bom_no, 'inspection_required')

    if purpose=="Material Transfer for Manufacture":
        stock_entry.to_warehouse = wip_warehouse
        stock_entry.project = work_order.project
    else:
        stock_entry.from_warehouse = wip_warehouse
        stock_entry.to_warehouse = work_order.fg_warehouse
        stock_entry.project = work_order.project

    stock_entry.set_stock_entry_type()
    get_bom_raw_materials(work_order_id, company,stock_entry,work_order)
    # stock_entry.set_serial_no_batch_for_finished_good()
    print(stock_entry.items)
    print("============================== NEW STOCK ENTRY ======================================")
    return stock_entry.as_dict()
