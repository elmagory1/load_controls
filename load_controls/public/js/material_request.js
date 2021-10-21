frappe.ui.form.on("Budget BOM References", {
    budget_bom: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]

        if(d.budget_bom){
            frappe.db.get_doc("Budget BOM",d.budget_bom)
                .then(doc => {
                    var fields = ["electrical_bom_raw_material","mechanical_bom_raw_material","fg_sellable_bom_raw_material",]
                for(var x=0;x<fields.length;x+=1){
                    for(var i=0;i<doc[fields[x]].length;i+=1){
                        cur_frm.add_child("items",{
                            item_code: doc[fields[x]][i].item_code,
                            item_name: doc[fields[x]][i].item_name,
                            description: doc[fields[x]][i].item_name,
                            qty: doc[fields[x]][i].qty,
                            uom: doc[fields[x]][i].uom,
                            warehouse: doc[fields[x]][i].warehouse,
                            rate: doc[fields[x]][i].rate,
                            budget_bom_rate: doc[fields[x]][i].rate,
                        })
                        cur_frm.refresh_field("items")
                    }
                }

            })
        }

    }
})