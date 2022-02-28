

frappe.ui.form.on("Purchase Receipt", {
    onload_post_render: function () {
        if(cur_frm.is_new() && cur_frm.doc.items.length > 0){
            frappe.call({
                method: "load_controls.doc_events.purchase_receipt.get_receive_qty",
                args: {
                    items: cur_frm.doc.items
                },
                callback: function (r) {
                        var objIndex = 0
console.log("RECEIVED QTY")
console.log(r.message)
                    for(var x=0;x<r.message.length;x+=1){
                         objIndex = cur_frm.doc.items.findIndex(obj => obj.name === r.message[x]['name'])

                        cur_frm.doc.items[objIndex].received_qty = r.message[x]['received_qty']
                        cur_frm.doc.items[objIndex].po_qty = r.message[x]['po_qty']
                       cur_frm.refresh_field("items")
                    }
                }
            })
        }
    }
})
frappe.ui.form.on("Purchase Receipt Item", {
    qty: function (frm, cdt, cdn) {
       var d = locals[cdt][cdn]

        if(d.qty > d.received_qty){
           d.qty = 0
           frappe.throw("Qty must not be greater than Received Qty")
            cur_frm.refresh_field(d.parentfield)
        }
    }
})