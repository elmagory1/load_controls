// Copyright (c) 2021, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gate Pass', {
	purchase_order: function(frm) {
        if(cur_frm.doc.purchase_order){
            frappe.db.get_doc("Purchase Order", cur_frm.doc.purchase_order)
                .then(doc => {
                    for(var i=0;i<doc.items.length;i+=1){
                             cur_frm.add_child("items", {
                                 item_code: doc.items[i].item_code,
                                 item_name: doc.items[i].item_name,
                                 description: doc.items[i].item_name,
                                 qty: doc.items[i].qty,
                                 uom: doc.items[i].uom,
                                 warehouse: doc.items[i].warehouse,
                                 rate:doc.items[i].rate,
                                 budget_bom_rate: doc.items[i].rate,
                             })
                             cur_frm.refresh_field("items")
                    }
            })
        }
	}
});
