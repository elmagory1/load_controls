// Copyright (c) 2022, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consumable Issue Note', {
	refresh: function(frm) {
	    if(cur_frm.doc.docstatus && !cur_frm.doc.stock_entry){
	          cur_frm.add_custom_button("Stock Entry", () => {
               cur_frm.call({
                  doc: cur_frm.doc,
                  method: "generate_se",
                  async:false,
                  callback: function () {
                      cur_frm.reload_doc()
                        frappe.show_alert({
                                    message: __('Stock Entry Created'),
                                    indicator: 'green'
                                }, 3);
                  }
              })
            })
        }

	}
});
frappe.ui.form.on('Consumable Issue Note Details', {
	qty: function(frm, cdt, cdn) {
	    var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)
        compute_total(cur_frm)
	},
    rate: function(frm) {
      var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)
        compute_total(cur_frm)
	}
});


function compute_total(cur_frm) {
    var total = 0
    for(var x=0;x<cur_frm.doc.items.length;x+=1){
        total += cur_frm.doc.items[x].amount
    }
    cur_frm.doc.total = total
    cur_frm.refresh_field("total")
}