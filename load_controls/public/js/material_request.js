frappe.ui.form.on("Budget BOM References", {
    budget_bom: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]

        if(d.budget_bom){
            if(!cur_frm.doc.items[0].item_code){
                cur_frm.clear_table("items")
                cur_frm.refresh_field("items")
            }
            frappe.db.get_doc("Budget BOM",d.budget_bom)
                .then(doc => {
                    var fields = ["electrical_bom_raw_material","mechanical_bom_raw_material","fg_sellable_bom_raw_material","electrical_bom_additiondeletion","mechanical_bom_addition_deletion"]
                for(var x=0;x<fields.length;x+=1){
                    for(var i=0;i<doc[fields[x]].length;i+=1){
                        if(!check_items(doc[fields[x]][i], cur_frm)) {
                            cur_frm.add_child("items", {
                                item_code: doc[fields[x]][i].item_code,
                                item_name: doc[fields[x]][i].item_name,
                                description: doc[fields[x]][i].item_name,
                                qty: doc[fields[x]][i].qty,
                                uom: doc[fields[x]][i].uom,
                                warehouse: doc[fields[x]][i].warehouse,
                                rate: doc[fields[x]][i].rate,
                                budget_bom_rate: doc[fields[x]][i].rate,
                                schedule_date: doc.expected_closing_date,
                                conversion_factor: 1,
                            })
                            cur_frm.refresh_field("items")
                        }
                    }
                }

            })
        }

    }
})
frappe.ui.form.on("Material Request", {
    onload_post_render: function () {
      cur_frm.remove_custom_button("Request for Quotation", "Create")
      cur_frm.remove_custom_button("Bill of Materials", "Get Items From")
      cur_frm.remove_custom_button("Sales Order", "Get Items From")
      cur_frm.remove_custom_button("Product Bundle", "Get Items From")
    },
    refresh: function (frm, cdt, cdn) {

         if(cur_frm.doc.docstatus){
            cur_frm.add_custom_button("Request for Quotation",() => {
                let d = new frappe.ui.Dialog({
                    title: 'Enter details',
                    fields: [
                        {
                            label: 'Item Group',
                            fieldname: 'item_group',
                            fieldtype: 'Link',
                            options: 'Item Group',
                        },
                        {
                            label: 'Brand',
                            fieldname: 'brand',
                            fieldtype: 'Link',
                            options: 'Brand',
                        },
                        {
                            label: 'Supplier',
                            fieldname: 'supplier',
                            fieldtype: 'Link',
                            options: 'Supplier',
                        }
                    ],
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        console.log(values);
                        frappe.call({
                              method: "load_controls.doc_events.request_for_quotation.generate_rfq",
                              args: {
                                  name:cur_frm.doc.name,
                                  values: values
                              },
                              async: false,
                                  callback: function (r) {
                                        frappe.set_route("Form", "Request for Quotation", r.message)
                                  }
                          })
                        d.hide();
                    }
                });

                d.show();

            })
        }
        cur_frm.set_query("budget_bom", "budget_bom_reference", () => {
            return {
                filters: {
                    status: "To Material Request"
                }
            }
        })
    if(cur_frm.is_new()){
         cur_frm.add_custom_button(__('Budget BOM'),
				function() {
            var budget_boms = []
            if(cur_frm.doc.budget_bom_reference){
                 budget_boms = Array.from(cur_frm.doc.budget_bom_reference, x => "budget_bom" in x ? x.budget_bom:"")
            }
                    var query_args = {
                        query:"load_controls.doc_events.material_request.get_budget_bom",
                        filters: {data: budget_boms}
                    }
					 var d = new frappe.ui.form.MultiSelectDialog({
                            doctype: "Opportunity",
                            target: cur_frm,
                            setters: [
                                {
                                    label: "Customer",
                                    fieldname: "party_name",
                                    fieldtype: "Link",
                                    options: "Customer",
                                    default: cur_frm.doc.party_name || undefined
                                }
                            ],
                            add_filters_group: 0,
                            date_field: "posting_date",
                            get_query() {
                                return query_args
                            },
                            action(selections) {
                                fetch_boms(cur_frm, selections)
                                d.dialog.hide()
                            }
                        });
				}, __("Get Items From"), "btn-default");
    }


    }
})

function fetch_boms(cur_frm, selections) {
    if(cur_frm.doc.items.length > 0 && !cur_frm.doc.items[0].item_code){
        cur_frm.clear_table("items")
        cur_frm.refresh_field("items")
    }
    if(selections.length > 0){
                    frappe.call({
                        method: "load_controls.doc_events.material_request.get_bb",
                        args: {
                            mr: selections
                        },
                        callback: function (r) {
                                for(var x=0;x<r.message[0].length;x+=1){
                                    cur_frm.add_child("items",r.message[0][x])
                                    cur_frm.refresh_field("items")
                                }
                                for(var x=0;x<r.message[1].length;x+=1){
                                    cur_frm.add_child("budget_bom_reference",r.message[1][x])
                                    cur_frm.refresh_field("budget_bom_reference")
                                }
                        }
                    })
                }
}