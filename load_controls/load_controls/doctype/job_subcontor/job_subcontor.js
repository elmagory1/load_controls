// Copyright (c) 2022, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Subcontor', {
    budget_bom: function () {
         if(cur_frm.doc.budget_bom){
            cur_frm.call({
              doc: cur_frm.doc,
              method: "get_budget_bom",
              async:false,
              callback: function (r) {
                  cur_frm.refresh_fields(['items','additional_cost'])
              }
          })
        }
    },
	refresh: function(frm) {
         if(cur_frm.doc.docstatus && !cur_frm.doc.purchase_order){
                  cur_frm.add_custom_button("Purchase Order", () => {
                   cur_frm.call({
                      doc: cur_frm.doc,
                      method: "generate_po",
                      async:false,
                      callback: function () {
                          cur_frm.reload_doc()
                            frappe.show_alert({
                                        message: __('Purchase Order Created'),
                                        indicator: 'green'
                                    }, 3);
                      }
                  })
                })
            }

	}
});
