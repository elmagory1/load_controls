
frappe.ui.form.on('Purchase Order', {
	refresh: function () {
        frappe.call({
            method: "load_controls.doc_events.purchase_order.check_gate_pass",
            args: {
                name: cur_frm.doc.name
            },
            callback: function (r) {
                if(!r.message && cur_frm.doc.docstatus){
                     cur_frm.add_custom_button(__("Gate Pass"), () => {
                         frappe.model.open_mapped_doc({
                            method: "load_controls.doc_events.purchase_order.generate_gate_pass",
                            frm: cur_frm
                        })

                    }, 'Create');
                }
            }
        })


    }

});