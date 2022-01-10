frappe.ui.form.on("Sales Order", {
    generate_project_code: function () {
        frappe.call({
                method: 'load_controls.doc_events.sales_order.generate_cost_centers',
                args: {
                    items: cur_frm.doc.items,
                    name: cur_frm.doc.name,
                    customer: cur_frm.doc.customer,
                    project_code: cur_frm.doc.cost_center ? cur_frm.doc.cost_center : "",
                    company: cur_frm.doc.company,
                },
                freeze: true,
                freeze_message: "Get Templates...",
                async: false,
                callback: (r) => {
                    cur_frm.reload_doc()
                }
        })
    },
    refresh: function (frm) {
        if(cur_frm.doc.docstatus) {
            cur_frm.add_custom_button('Material Request', () => {
                let query_args = {
                    query: "load_controls.doc_events.sales_order.get_budget_bom",
                    filters: {parent: cur_frm.doc.name}
                }
                new frappe.ui.form.MultiSelectDialog({
                    setters: {},
                    doctype: "Budget BOM",
                    target: cur_frm,
                    date_field: "posting_date",
                    get_query(){
                        return query_args;
                    },
                    action(selections) {
                        frappe.call({
                            method: "load_controls.doc_events.sales_order.generate_mr",
                            args: {
                                budget_boms: selections,
                                schedule_date: cur_frm.doc.delivery_date,
                                transaction_date: cur_frm.doc.transaction_date,
                                so_name: cur_frm.doc.name
                            },
                            async:false,
                            callback: function (r) {
                                 frappe.set_route("Form", "Material Request", r.message);
                            }
                        })
                    }
                })
            }).css('background-color','#8B4513').css('color','white').css('font-weight','bold')
        }
    }
})