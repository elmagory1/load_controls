

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
                                for(var x=0;x<r.message.length;x+=1){
                                    cur_frm.add_child("items",r.message[x])
                                    cur_frm.refresh_fields("items")
                                }
                        }
                    })
                }
            }
        });

    }
})