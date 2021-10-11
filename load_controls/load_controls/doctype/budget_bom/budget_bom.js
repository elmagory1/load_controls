// Copyright (c) 2021, jan and contributors
// For license information, please see license.txt
var workstation = ""
var operation = ""
var routing = ""
var has_quotation = false
var generating_quotation = false
frappe.ui.form.on('Budget BOM', {
	refresh: function(frm) {
	    if(!generating_quotation){
	        cur_frm.call({
                doc: cur_frm.doc,
                method: 'get_quotation',
                args: {},
                freeze: true,
                freeze_message: "Get Quotation...",
                async:false,
                callback: (r) => {
                    console.log("HAS QUOTATION")
                    has_quotation = r.message
                }
            })
        }

	        frappe.db.get_single_value("Manufacturing Settings","default_workstation")
                .then(d_workstation => {
                    workstation = d_workstation

            })
            frappe.db.get_single_value("Manufacturing Settings","default_operation")
                .then(d_operation => {
                    operation = d_operation

            })
            frappe.db.get_single_value("Manufacturing Settings","default_routing")
                .then(d_routing => {
                    routing = d_routing

            })
                            console.log(" BUTTON")

        if(cur_frm.doc.docstatus && cur_frm.doc.status === "To Quotation" && !has_quotation){
	            frm.add_custom_button(__("Quotation"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'generate_quotation',
                        args: {},
                        freeze: true,
                        freeze_message: "Generating Quotation...",
                        callback: (r) => {
                            generating_quotation = true
                            cur_frm.reload_doc()
                            frappe.set_route("Form", "Quotation", r.message);
                        }
                    })
                })
        } else if(cur_frm.doc.docstatus && cur_frm.doc.status === "To Design"){
	            frm.add_custom_button(__("Amend Quotation"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'amend_quotation',
                        args: {},
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                })
                frm.add_custom_button(__("Approve"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'action_to_design',
                        args: {
                            status: "Approve"
                        },
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }, "Action")
            frm.add_custom_button(__("Update"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'action_to_design',
                        args: {
                            status: "Update"
                        },
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }, "Action")


        } else if(cur_frm.doc.docstatus && cur_frm.doc.status === "Pending"){

                frm.add_custom_button(__("Approve"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'action_to_design',
                        args: {
                            status: "Approve"
                        },
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }, "Action")
            frm.add_custom_button(__("Reject"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'action_to_design',
                        args: {
                            status: "Reject"
                        },
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }, "Action")


        }
        cur_frm.set_df_property("electrical_bom_raw_material", "read_only", !cur_frm.doc.quotation_amended)
        cur_frm.set_df_property("mechanical_bom_raw_material", "read_only", !cur_frm.doc.quotation_amended)
        cur_frm.set_df_property("fg_sellable_bom_raw_material", "read_only", !cur_frm.doc.quotation_amended)
        var fields = ["item_code","item_name","qty","valuation_rate","rate","amount","available_qty", "discount", "uom", "batch", "warehouse"]
        for(var x=0;x<fields.length;x+=1){
            console.log(fields[x])
            var field = frappe.meta.get_docfield("Budget BOM Raw Material", fields[x], cur_frm.doc.name);
            field.read_only = !cur_frm.doc.quotation_amended
        }

    },
	onload_post_render: function(frm) {
	    if(cur_frm.is_new()){

            cur_frm.add_child("electrical_bom_details", {
                workstation: workstation,
                operation: operation
            })
            cur_frm.add_child("mechanical_bom_details", {
                workstation:workstation,
                operation: operation
            })
            cur_frm.add_child("fg_sellable_bom_details", {
                workstation: workstation,
                routing:routing
            })
            cur_frm.get_field("electrical_bom_details").grid.cannot_add_rows = true;
            cur_frm.get_field("mechanical_bom_details").grid.cannot_add_rows = true;
            cur_frm.get_field("fg_sellable_bom_details").grid.cannot_add_rows = true;

            cur_frm.get_field("electrical_bom_details").grid.only_sortable();
            cur_frm.get_field("mechanical_bom_details").grid.only_sortable();
            cur_frm.get_field("fg_sellable_bom_details").grid.only_sortable();

            cur_frm.refresh_field("electrical_bom_details")
            cur_frm.refresh_field("mechanical_bom_details")
            cur_frm.refresh_field("fg_sellable_bom_details")
        }


	},
    electrical_item_template: function(frm) {
        get_template(cur_frm.doc.electrical_item_template, "electrical_bom_raw_material")
	},
    mechanical_item_template: function(frm) {
        get_template(cur_frm.doc.mechanical_item_template, "mechanical_bom_raw_material")
	},
    fg_sellable_item_template: function(frm) {
        get_template(cur_frm.doc.fg_sellable_item_template, "fg_sellable_bom_raw_material")
	},

     total_operation_cost: function(frm) {
        compute_total_cost_expense(cur_frm)
	},
    additional_operation_cost: function(frm) {
        compute_total_cost_expense(cur_frm)
	},
    discount: function(frm) {
        compute_total_cost_expense(cur_frm)
	},
    margin_: function(frm) {
        compute_total_cost_expense(cur_frm)
	},
});

frappe.ui.form.on('Budget BOM Raw Material', {
    qty: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)
        compute_total_cost(cur_frm)
        compute_total_cost_expense(cur_frm)

	},
    rate: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)

        compute_total_cost(cur_frm)
                compute_total_cost_expense(cur_frm)

	},
});
frappe.ui.form.on('Additional Operational Cost', {
    amount: function(frm, cdt, cdn) {
        var total=0
       for(var ii=0;ii<cur_frm.doc.additional_operation_cost.length;ii+=1){
            total += cur_frm.doc.additional_operation_cost[ii].amount
        }
        cur_frm.doc.total_additional_operation_cost = total
        cur_frm.refresh_field("total_additional_operation_cost")
	}
});
function compute_total_cost_expense(cur_frm) {
   cur_frm.doc.total_cost = ((cur_frm.doc.total_operation_cost + cur_frm.doc.additional_operation_cost) - cur_frm.doc.discount) + cur_frm.doc.margin_
    cur_frm.refrsh_field("total_cost")
}
function compute_total_cost(cur_frm) {
    var fieldnames = ['electrical_bom_raw_material','mechanical_bom_raw_material','fg_sellable_bom_raw_material']
    var total = 0
    for(var i=0;i<fieldnames.length;i+=1){
        if(cur_frm.doc[fieldnames[i]]){
            for(var ii=0;ii<cur_frm.doc[fieldnames[i]].length;ii+=1){
                total += cur_frm.doc[fieldnames[i]][ii].amount
            }
        }

    }
    cur_frm.doc.total_raw_material_cost = total
    cur_frm.refresh_field("total_raw_material_cost")
}
function get_template(template_name, raw_material_table){
    frappe.db.get_doc("BOM Item Template", template_name)
        .then(doc => {
            for(var x=0;x<doc.items.length;x+=1){
                cur_frm.add_child(raw_material_table, {
                    item_code: doc.items[x].item_code,
                    item_name: doc.items[x].item_name,
                    uom: doc.items[x].uom,
                    qty: doc.items[x].qty,
                })
                cur_frm.refresh_field(raw_material_table)
            }

    })
}