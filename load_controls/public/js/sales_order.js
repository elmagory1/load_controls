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
    }
})