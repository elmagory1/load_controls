frappe.ui.form.on("Opportunity", {
    refresh: function () {
        cur_frm.set_query("project", ()=>{
            return {
                filters: {
                    disabled: 0
                }
            }
        })
        if(!cur_frm.is_new()){
           cur_frm.remove_custom_button("Quotation", "Create")
            cur_frm.remove_custom_button("Supplier Quotation", "Create")
            cur_frm.remove_custom_button("Request For Quotation", "Create")
            cur_frm.remove_custom_button("Budget BOM", "Create")
            if(cur_frm.doc.status === 'Qualified') {
             cur_frm.add_custom_button(__('Budget BOM'),
				function() {
                    // frappe.model.open_mapped_doc({
                    //     method: "load_controls.doc_events.opportunity.make_bb",
                    //     frm: cur_frm
                    // })
                    var query_args = {
                        query:"load_controls.doc_events.opportunity.get_items",
                        filters: {parent: cur_frm.doc.name}
                    }
                    new frappe.ui.form.MultiSelectDialog({
                        doctype: "Opportunity Item",
                        target: cur_frm,
                        setters: {
                            item_name: null
                        },
                        add_filters_group: 1,
                        date_field: "transaction_date",
                        get_query() {
                            return query_args
                        },
                        action(selections) {
                            if(selections.length > 1){
                                frappe.throw("Please Select Only 1 Item")
                            }
                            console.log("SELECTIONS")
                            console.log(selections)
                            if(selections.length > 0){
                                 frappe.call({
                                    method: 'load_controls.doc_events.opportunity.generate_budget_bom',
                                    args: {
                                        selections: selections,
                                        name: cur_frm.doc.name
                                    },
                                    freeze: true,
                                    freeze_message: "Generating Budget BOM...",
                                    callback: (r) => {
                                        frappe.set_route("Form", "Budget BOM", r.message);

                                    }
                                })
                            }

                        }
                    });
				}, __("Create"));
            }


        }

    }
})