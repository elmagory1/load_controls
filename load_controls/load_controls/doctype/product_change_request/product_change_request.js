// Copyright (c) 2022, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product Change Request Addition', {
    addition_add: function (frm,cdt, cdn) {
        var d =locals[cdt][cdn]
        d.target_warehouse = cur_frm.doc.target_warehouse
        cur_frm.refresh_field(d.parentfield)

    },
    item: function (frm, cdt ,cdn) {
        var d = locals[cdt][cdn]
        if(d.item && d.target_warehouse){
           cur_frm.call({
            doc: cur_frm.doc,
            method: "update_specific_row_available_stock",
            async: false,
            args: {
                item_code: d.item,
                warehouse: d.target_warehouse
            },
            callback: function (r) {
                 d.available_qty = r.message
                cur_frm.refresh_field(d.parentfield)
            }
        })
        }

    },
    target_warehouse: function (frm, cdt,cdn) {
       var d = locals[cdt][cdn]
        if(d.item && d.target_warehouse){
           cur_frm.call({
            doc: cur_frm.doc,
            method: "update_specific_row_available_stock",
            async: false,
            args: {
                item_code: d.item,
                warehouse: d.target_warehouse
            },
            callback: function (r) {
                d.available_qty = r.message
                cur_frm.refresh_field(d.parentfield)
            }
        })
        }
    }
})

frappe.ui.form.on('Product Change Request Deletion', {
    deletion_add: function (frm,cdt, cdn) {
        var d =locals[cdt][cdn]
        d.source_warehouse = cur_frm.doc.source_warehouse
        cur_frm.refresh_field(d.parentfield)
    },
    item: function (frm, cdt ,cdn) {
                var d = locals[cdt][cdn]
        if(d.item && d.source_warehouse){
           cur_frm.call({
            doc: cur_frm.doc,
            method: "update_specific_row_available_stock",
            async: false,
            args: {
                item_code: d.item,
                warehouse: d.source_warehouse
            },
            callback: function (r) {
                d.available_qty = r.message
                cur_frm.refresh_field(d.parentfield)
            }
        })
        }

    },
    source_warehouse: function (frm, cdt,cdn) {
       var d = locals[cdt][cdn]
        if(d.item && d.source_warehouse){
           cur_frm.call({
            doc: cur_frm.doc,
            method: "update_specific_row_available_stock",
            async: false,
            args: {
                item_code: d.item,
                warehouse: d.source_warehouse
            },
            callback: function (r) {
                 d.available_qty = r.message
                cur_frm.refresh_field(d.parentfield)
            }
        })
        }
    }
})
var items = []
frappe.ui.form.on('Product Change Request', {

    source_warehouse: function () {
        if(cur_frm.doc.source_warehouse) {

            for (var x = 0; x < cur_frm.doc.deletion.length; x += 1) {
                cur_frm.doc.deletion[x].source_warehouse = cur_frm.doc.source_warehouse
                cur_frm.refresh_field("deletion")
            }
        }
         cur_frm.call({
            doc: cur_frm.doc,
            method: "update_available_stock",
            async: false,
            callback: function (r) {
                cur_frm.refresh_field("deletion")
            }
        })
    },
      target_warehouse: function () {
        if(cur_frm.doc.target_warehouse){
             for(var x=0;x<cur_frm.doc.addition.length;x+=1){
              cur_frm.doc.addition[x].target_warehouse = cur_frm.doc.target_warehouse
              cur_frm.refresh_field("addition")
            }
        }
         cur_frm.call({
            doc: cur_frm.doc,
            method: "update_available_stock",
            async: false,
            callback: function (r) {
                cur_frm.call({
            doc: cur_frm.doc,
            method: "update_available_stock",
            async: false,
            callback: function (r) {
                cur_frm.refresh_field("addition")
            }
        })
            }
        })
    },
    budget_bom: function () {
        if(cur_frm.doc.budget_bom){
            cur_frm.call({
              doc: cur_frm.doc,
              method: "get_budget_bom",
              async:false,
              callback: function (r) {
                  cur_frm.doc.total_incoming_value = r.message[0]
                  cur_frm.doc.total_outgoing_value = r.message[1]
                  cur_frm.doc.total_value_difference = r.message[0] - r.message[1]
                  cur_frm.doc.sales_order = r.message[2]
                  cur_frm.doc.project_code = r.message[3]
                  cur_frm.refresh_fields(['total_incoming_value','total_outgoing_value','total_value_difference','addition','deletion',"sales_order","project_code"])
              }
          })
            cur_frm.call({
            doc: cur_frm.doc,
            method: "get_bb_items",
            async: false,
            callback: function (r) {
                console.log(r.message)
               cur_frm.set_query("item","addition", () => {
                   return {
                       filters: [
                           ["name", "in", r.message[0]]
                       ]
                   }
               })
                cur_frm.set_query("item","deletion", () => {
                   return {
                       filters: [
                           ["name", "in", r.message[1]]
                       ]
                   }
               })
            }
        })
        }

    },
    work_order: function () {
         cur_frm.call({
            doc: cur_frm.doc,
            method: "get_bb_items",
            async: false,
            callback: function (r) {
                items = r.message
            }
        })
    },
	refresh: function(frm) {
        cur_frm.call({
            doc: cur_frm.doc,
            method: "get_bb_items",
            async: false,
            callback: function (r) {
                items = r.message
            }
        })
        cur_frm.set_query("item","deletion", () => {
                   return {
                       filters: [
                           ["name", "in", items]
                       ]
                   }
               })
	    if(cur_frm.doc.docstatus && cur_frm.doc.status === 'Approved') {

	        if(!cur_frm.doc.material_request){
	            cur_frm.add_custom_button("Material Request", () => {
                cur_frm.call({
                doc: cur_frm.doc,
                method: "generate_mr",
                async: false,
                callback: function () {
                    cur_frm.reload_doc()
                    frappe.show_alert({
                        message: __('Material Request Created'),
                        indicator: 'green'
                    }, 3);
                }
            })})
            }


        if(!cur_frm.doc.stock_entry){

                cur_frm.add_custom_button("Stock Entry", () => {
                    cur_frm.call({
                    doc: cur_frm.doc,
                    method: "generate_se",
                    async: false,
                    callback: function () {
                        cur_frm.reload_doc()
                        frappe.show_alert({
                            message: __('Stock Entry Created'),
                            indicator: 'green'
                        }, 3);
                    }
                })
            })
            }
        }
        if(cur_frm.doc.docstatus && cur_frm.doc.status === 'Pending'){
         cur_frm.add_custom_button("Approve", () => {
                   cur_frm.call({
                      doc: cur_frm.doc,
                      method: "change_status",
                     args:{
                          status: "Approved"
                     },
                      async:false,
                      callback: function (r) {
                          cur_frm.reload_doc()
                      }
                  })
            }, "Action")
         cur_frm.add_custom_button("Reject", () => {
                  cur_frm.call({
                      doc: cur_frm.doc,
                      method: "change_status",
                      args:{
                          status: "Declined"
                     },
                      async:false,
                      callback: function (r) {
                        cur_frm.reload_doc()
                      }
                  })
            },"Action")
        }

	}
});
