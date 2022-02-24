
frappe.ui.form.on("Request for Quotation", {
    fetch_mr: function () {
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
                        }
                    })
                }
            }
        });

    }
})