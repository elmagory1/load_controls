import frappe, json

from frappe import _
def on_submit_pl(doc, method):
    if doc.work_order:
        wo = frappe.get_doc("Work Order", doc.work_order)
        for i in doc.locations:
            woi = frappe.db.sql(""" SELECT * FROm `tabWork Order Item` WHERE name=%s""", i.work_order_item, as_dict=1)
            if len(woi) > 0:
                frappe.db.sql(""" UPDATE `tabWork Order Item` SET picked_qty=%s WHERE name=%s """,(woi[0].picked_qty + i.qty,i.work_order_item))
                frappe.db.commit()


def on_cancel_pl(doc, method):
    if doc.work_order:
        wo = frappe.get_doc("Work Order", doc.work_order)
        for i in doc.locations:
            woi = frappe.db.sql(""" SELECT * FROm `tabWork Order Item` WHERE name=%s""", i.work_order_item, as_dict=1)
            if len(woi) > 0:
                frappe.db.sql(""" UPDATE `tabWork Order Item` SET picked_qty=%s WHERE name=%s """,(woi[0].picked_qty - i.qty,i.work_order_item))
                frappe.db.commit()



def validate_item_locations(pick_list):
    if not pick_list.locations:
        frappe.throw(_("Add items in the Item Locations table"))

def stock_entry_exists(pick_list_name):
    return frappe.db.exists('Stock Entry', {
        'pick_list': pick_list_name
	})

@frappe.whitelist()
def create_stock_entry(pick_list):
    pick_list = frappe.get_doc(json.loads(pick_list))
    validate_item_locations(pick_list)

    if stock_entry_exists(pick_list.get('name')):
        return frappe.msgprint(_('Stock Entry has been already created against this Pick List'))

    stock_entry = frappe.new_doc('Stock Entry')
    stock_entry.pick_list = pick_list.get('name')
    stock_entry.purpose = pick_list.get('purpose')
    stock_entry.set_stock_entry_type()

    if pick_list.get('work_order'):
        stock_entry = update_stock_entry_based_on_work_order(pick_list, stock_entry)
    elif pick_list.get('material_request'):
        stock_entry = update_stock_entry_based_on_material_request(pick_list, stock_entry)
    else:
        stock_entry = update_stock_entry_items_with_no_reference(pick_list, stock_entry)

    stock_entry.set_actual_qty()
    stock_entry.calculate_rate_and_amount()

    return stock_entry.as_dict()


def update_stock_entry_based_on_material_request(pick_list, stock_entry):
    for location in pick_list.locations:
        target_warehouse = None
        if location.material_request_item:
            target_warehouse = frappe.get_value('Material Request Item',
                location.material_request_item, 'warehouse')
        item = frappe._dict()
        update_common_item_properties(item, location)
        item.t_warehouse = target_warehouse
        stock_entry.append('items', item)

    return stock_entry

def update_stock_entry_items_with_no_reference(pick_list, stock_entry):
    for location in pick_list.locations:
        item = frappe._dict()
        update_common_item_properties(item, location)

        stock_entry.append('items', item)

    return stock_entry

def update_common_item_properties(item, location):
    item.item_code = location.item_code if not location.alternative_item else location.alternative_item
    item.s_warehouse = location.warehouse
    item.qty = location.picked_qty * location.conversion_factor
    item.transfer_qty = location.picked_qty
    item.uom = location.uom
    item.conversion_factor = location.conversion_factor
    item.stock_uom = location.stock_uom
    item.material_request = location.material_request
    item.serial_no = location.serial_no
    item.batch_no = location.batch_no
    item.material_request_item = location.material_request_item

def update_stock_entry_based_on_work_order(pick_list, stock_entry):
    work_order = frappe.get_doc("Work Order", pick_list.get('work_order'))

    stock_entry.work_order = work_order.name
    stock_entry.company = work_order.company
    stock_entry.from_bom = 1
    stock_entry.bom_no = work_order.bom_no
    stock_entry.use_multi_level_bom = work_order.use_multi_level_bom
    stock_entry.fg_completed_qty = pick_list.for_qty
    if work_order.bom_no:
        stock_entry.inspection_required = frappe.db.get_value('BOM',
            work_order.bom_no, 'inspection_required')

    is_wip_warehouse_group = frappe.db.get_value('Warehouse', work_order.wip_warehouse, 'is_group')
    if not (is_wip_warehouse_group and work_order.skip_transfer):
        wip_warehouse = work_order.wip_warehouse
    else:
        wip_warehouse = None
    stock_entry.to_warehouse = wip_warehouse

    stock_entry.project = work_order.project

    for location in pick_list.locations:
        item = frappe._dict()
        update_common_item_properties(item, location)
        item.t_warehouse = wip_warehouse

        stock_entry.append('items', item)

    return stock_entry