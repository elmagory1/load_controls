
frappe.ui.form.on("Request for Quotation Item", {
    items_add: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(cur_frm.doc.warehouse){
            d.warehouse = cur_frm.doc.warehouse
            cur_frm.refresh_field(d.parentfield)
        }
    },
    warehouse: function (frm, cdt, cdn) {
        var d=locals[cdt][cdn]
        if(d.warehouse){
            cur_frm.trigger("refresh_available_stock")
        }
    }
})
frappe.ui.form.on("Request for Quotation", {
    warehouse: function () {
      if(cur_frm.doc.warehouse){
          for(var x=0;x<cur_frm.doc.items.length;x+=1){
              cur_frm.doc.items[x].warehouse = cur_frm.doc.warehouse
              cur_frm.refresh_field("items")
          }
           cur_frm.trigger("refresh_available_stock")
      }
    },
    fetch_mr: function () {
        var names = []
        if(cur_frm.doc.references && cur_frm.doc.references.length > 0){

          names = Array.from(cur_frm.doc.references, x => "material_request" in x ? x.material_request:"")

        }
        if(cur_frm.doc.items.length > 0 && !cur_frm.doc.items[0].item_code){
            cur_frm.clear_table("items")
            cur_frm.refresh_field("items")
        }
        if(cur_frm.doc.suppliers.length > 0 && !cur_frm.doc.suppliers[0].item_code){
            cur_frm.clear_table("suppliers")
            cur_frm.refresh_field("suppliers")
        }
        var d = new frappe.ui.form.MultiSelectDialog({
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
                        name: ['not in', names],
                    }
                }
            },
            action(selections) {
                if(selections.length > 0){
                    frappe.call({
                        method: "load_controls.doc_events.request_for_quotation.get_mr",
                        args: {
                            mr: selections,
                            item_group: cur_frm.doc.item_group ? cur_frm.doc.item_group : "",
                            brand: cur_frm.doc.brand ? cur_frm.doc.brand : "",
                            supplier: cur_frm.doc.supplier ? cur_frm.doc.supplier : "",
                        },
                        callback: function (r) {
                            if(r.message[3]){
                                cur_frm.doc.warehouse = r.message[3]
                                cur_frm.refresh_field("warehouse")
                            }
                                for(var x=0;x<r.message[0].length;x+=1){
                                    cur_frm.add_child("items",r.message[0][x])
                                    cur_frm.refresh_field("items")
                                }

                                for(var xx=0;xx<r.message[1].length;xx+=1){
                                    cur_frm.add_child("budget_bom_reference",{
                                        budget_bom: r.message[1][xx]
                                    })
                                    cur_frm.refresh_field("budget_bom_reference")
                                }
                                 for(var x=0;x<r.message[2].length;x+=1){
                                    cur_frm.add_child("suppliers",{"supplier": r.message[2][x]})
                                    cur_frm.refresh_field("suppliers")
                                }
                                for(var x=0;x<selections.length;x+=1){
                                    cur_frm.add_child("references",{"material_request": selections[x]})
                                    cur_frm.refresh_field("references")
                                }
                                cur_dialog.hide()
                        }
                    })
                }
            }
        });

    },
    refresh: function () {
        cur_frm.fields_dict["items"].grid.add_custom_button(__('Refresh Available Stock'),
			function() {
	        cur_frm.trigger("refresh_available_stock")
        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px').css('font-weight','bold')

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