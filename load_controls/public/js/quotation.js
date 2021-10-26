
function update_items(item, cur_frm) {
        for(var x=0;x<cur_frm.doc.items.length;x+=1){
            var item_row = cur_frm.doc.items[x]
            console.log(item_row.item_code)
            console.log(item)
            if(item_row.item_code === item.item_code){
                item_row.rate = item.total_cost
                item_row.amount = item.total_cost * item_row.qty
                cur_frm.refresh_field("items")
                cur_frm.trigger("rate")
            }
        }
        compute_total(cur_frm)
}
function compute_total(cur_frm) {
    var total = 0
    $.each(cur_frm.doc.items || [], function(i, items) {
        total += items.amount
    });
    cur_frm.doc.total = total
    cur_frm.doc.grand_total = total - cur_frm.doc.discount_amount
    cur_frm.doc.rounded_total =  cur_frm.doc.grand_total
    cur_frm.refresh_fields(["total",'grand_total','rounded_total'])
}
frappe.ui.form.on('Quotation', {
	update_cost: function(frm) {
	    cur_frm.clear_table("payment_schedule")
	    cur_frm.refresh_field("payment_schedule")
	    frappe.call({
            method: "load_controls.doc_events.quotation.get_updated_costs",
            args: {
                budget_boms: cur_frm.doc.budget_bom_reference ? cur_frm.doc.budget_bom_reference : []
            },
            async: false,
            callback: function (r) {
                console.log(r.message)
                for(var x=0;x<r.message.length;x+=1){
                    update_items(r.message[0][x], cur_frm)
                }
            }
        })
    },
	refresh: function(frm) {
	    cur_frm.set_query("budget_bom", "budget_bom_reference", () => {
            return {
                filters: {
                    status: "To Quotation"
                }
            }
        })
         cur_frm.set_query("opportunity", "budget_bom_opportunity", () => {
            return {
                filters: {
                    status: "Open"
                }
            }
        })
        cur_frm.fields_dict["items"].grid.add_custom_button(__('Update Cost'),
			function() {
	        cur_frm.trigger("update_cost")
        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px').css('font-weight','bold')

        cur_frm.add_custom_button(__('Opportunity with Budget BOM'),
				function() {
                    var query_args = {
                        query:"load_controls.doc_events.quotation.get_opportunity",
                        filters: {}
                    }
					 var d = new frappe.ui.form.MultiSelectDialog({
                            doctype: "Opportunity",
                            target: cur_frm,
                            setters: [
                                {
                                    label: "Customer",
                                    fieldname: "party_name",
                                    fieldtype: "Link",
                                    options: "Customer",
                                    default: cur_frm.doc.party_name || undefined
                                }
                            ],
                            add_filters_group: 0,
                            date_field: "posting_date",
                            get_query() {
                                return query_args
                            },
                            action(selections) {
                                fetch_boms(cur_frm, selections)
                                d.dialog.hide()
                            }
                        });
				}, __("Get Items From"), "btn-default");
    }
})

function fetch_boms(cur_frm, selections) {
    for(var x=0;x<selections.length;x+=1){
        var check_opp = check_opportunity(selections[x])
        if(!check_opp){
            console.log(check_opp)
            console.log("NISULOD UNA")
            cur_frm.add_child("budget_bom_opportunity",{
                opportunity: selections[x]
            })
            cur_frm.refresh_field("budget_bom_opportunity")

            frappe.db.get_list('Budget BOM', {
                filters: {
                   opportunity: selections[x]
                }
            }).then(records => {
                if(records.length > 0){

                    frappe.db.get_doc('Budget BOM', null, { opportunity: selections[x]})
                    .then(doc => {
                        cur_frm.doc.party_name = doc.customer
                        cur_frm.doc.customer_name = doc.customer_name
                        cur_frm.refresh_field("party_name")
                        cur_frm.refresh_field("customer_name")
                        cur_frm.add_child("budget_bom_reference",{
                            budget_bom: doc.name
                        })
                        cur_frm.refresh_field("budget_bom_reference")

                        cur_frm.clear_table("items")
                        if(!check_items(doc.fg_sellable_bom_details[0], cur_frm)){
                              cur_frm.add_child("items",{
                            "item_code": doc.fg_sellable_bom_details[0].item_code,
                            "item_name": doc.fg_sellable_bom_details[0].item_name,
                            "description": doc.fg_sellable_bom_details[0].item_name,
                            "qty": doc.fg_sellable_bom_details[0].qty,
                            "uom": doc.fg_sellable_bom_details[0].uom,
                            "rate": doc.total_cost,
                            "amount": doc.total_cost * doc.fg_sellable_bom_details[0].qty,
                        })
                        cur_frm.refresh_field("items")
                        }



                    })
                }
            })
        }



    }
}
function check_items(item, cur_frm) {
        for(var x=0;x<cur_frm.doc.items.length;x+=1){
            var item_row = cur_frm.doc.items[x]
            if(item_row.item_code === item.item_code){
                item_row.qty += item.qty
                cur_frm.refresh_field("items")
                return true
            }
        }
        return false
}
function check_opportunity(name) {
    console.log("NAAAAAAAAAME")
    console.log(name)
    if(cur_frm.doc.budget_bom_opportunity){
        console.log("WAAAAAAAAT")
        for(var x=0;x<cur_frm.doc.budget_bom_opportunity.length;x+=1){
            var item_row = cur_frm.doc.budget_bom_opportunity[x]
            console.log(item_row.opportunity)
            console.log(name)
            if(item_row.opportunity === name){
                console.log("AFTER CHECK")
                return true
            }
        }
    }

        return false
}