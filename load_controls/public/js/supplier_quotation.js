frappe.ui.form.on("Supplier Quotation Item", {
    warehouse: function (frm, cdt, cdn) {
        var d=locals[cdt][cdn]
        if(d.warehouse){
            cur_frm.trigger("refresh_available_stock")
        }
    }
})
cur_frm.cscript.refresh_available_stock = function () {
     frappe.call({
            method: "load_controls.load_controls.doctype.budget_bom.budget_bom.set_available_qty",
            args: {
                items: cur_frm.doc.items
            },
            callback: function (r) {
                var objIndex = 0
               for(var x=0;x<r.message.length;x+=1){
                    console.log("NAA")
                   objIndex = cur_frm.doc.items.findIndex(obj => obj.name === r.message[x]['name'])

                    cur_frm.doc.items[objIndex].available_qty = r.message[x]['available_qty']
                    cur_frm.doc.items[objIndex].required_qty = r.message[x]['qty'] - r.message[x]['available_qty']
                   cur_frm.refresh_field("items")
               }
            }
        })
}

frappe.ui.form.on("Supplier Quotation", {
    fetch_material_request: function () {
        if(cur_frm.doc.items.length > 0 && !cur_frm.doc.items[0].item_code){
            cur_frm.clear_table("items")
            cur_frm.refresh_field("items")
        }
        if(!cur_frm.doc.supplier) {
            frappe.throw("Please select supplier first")
        }
        new frappe.ui.form.MultiSelectDialog({
            doctype: "Material Request",
            target: cur_frm,
            setters: {},
            add_filters_group: 1,
            date_field: "transaction_date",
            get_query() {
                return {
                    filters: {
                        docstatus: ['!=', 2],
                        status: ['=', 'Pending'],
                    }
                }
            },
            action(selections) {
                if(selections.length > 0){
                    frappe.call({
                        method: "load_controls.doc_events.supplier_quotation.get_mr",
                        args: {
                            supplier: cur_frm.doc.supplier,
                            mr: selections,
                        },
                        callback: function (r) {
                                for(var x=0;x<r.message[0].length;x+=1){
                                    cur_frm.add_child("items",r.message[0][x])
                                    cur_frm.refresh_fields("items")
                                }

                                for(var xx=0;xx<r.message[1].length;xx+=1){
                                    cur_frm.add_child("budget_bom_reference",{
                                        budget_bom: r.message[1][xx]
                                    })
                                    cur_frm.refresh_fields("budget_bom_reference")
                                }
                        }
                    })
                }
            }
        });

    }.,
    refresh: function () {
         cur_frm.fields_dict["items"].grid.add_custom_button(__('Refresh Available Stock'),
			function() {
	        cur_frm.trigger("refresh_available_stock")
        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px').css('font-weight','bold')

    }
})