
frappe.ui.form.on("Pick List", {
    refresh: function () {
        	if(cur_frm.doc.docstatus){
                cur_frm.remove_custom_button("Stock Entry",'Create')
                cur_frm.add_custom_button(__('Stock Entry'), () => cur_frm.trigger('create_stock_entry'), __('Create'));
            }

    },
    create_stock_entry: (frm) => {
		frappe.xcall('load_controls.doc_events.pick_list.create_stock_entry', {
			'pick_list': frm.doc,
		}).then(stock_entry => {
			frappe.model.sync(stock_entry);
			frappe.set_route("Form", 'Stock Entry', stock_entry.name);
		});
	},
})