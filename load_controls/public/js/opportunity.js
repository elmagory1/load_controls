frappe.ui.form.on("Opportunity", {
    refresh: function () {
         cur_frm.add_custom_button(__('Budget BOM'),
				function() {
					frappe.model.open_mapped_doc({
                        method: "load_controls.doc_events.opportunity.make_bb",
                        frm: cur_frm
                    })
				}, __("Create"));
    }
})