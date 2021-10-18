// Copyright (c) 2021, jan and contributors
// For license information, please see license.txt
var workstation = ""
var electrical_operation = ""
var mechanical_operation = ""
var fg_sellable_operation = ""
var routing = ""
var has_quotation = false
var has_so = false
var generating_quotation = false
var table_name = ""
var net_hour_rate = 0
var raw_material_warehouse = 0
cur_frm.cscript.item_templates = function () {
    var d = new frappe.ui.form.MultiSelectDialog({
        doctype: "BOM Item Template",
        target: this.cur_frm,
        setters: {
            description: null
        },
        add_filters_group: 1,
        date_field: "posting_date",
        get_query() {
            return {
                filters: { docstatus: ['!=', 2] }
            }
        },
        action(selections) {
            console.log(d)

            get_template(selections, table_name, cur_frm)
            d.dialog.hide()
        }
    });
}
cur_frm.cscript.generate_item_template = function () {
    let d = new frappe.ui.Dialog({
        title: 'Enter details',
        fields: [
            {
                label: 'Description',
                fieldname: 'description',
                fieldtype: 'Data',
                reqd: 1
            }
        ],
        primary_action_label: 'Submit',
        primary_action(values) {
            console.log(values)
            frappe.call({
                method: "load_controls.load_controls.doctype.budget_bom.budget_bom.generate_item_templates",
                args: {
                    items: cur_frm.doc[table_name],
                    description: values.description
                },
                async: false,
                callback: function (r) {
                        frappe.show_alert({
                            message:__('BOM Item Template Created'),
                            indicator:'green'
                        }, 3);
                }
            })
            d.hide();
        }
    });

    d.show();

}
frappe.ui.form.on('Budget BOM', {
	refresh: function(frm) {
	    //ELECTRICAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL
	    cur_frm.fields_dict["electrical_bom_raw_material"].grid.add_custom_button(__('Refresh Available Stock'),
			function() {
	        cur_frm.trigger("refresh_electrical_available_stock")
        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px')

	    cur_frm.fields_dict["electrical_bom_raw_material"].grid.add_custom_button(__('Generate Item Template'),
			function() {
	        table_name = "electrical_bom_raw_material"
	        cur_frm.trigger("generate_item_template")
        }).css('background-color','#CCCC00').css('margin-left','10px')

        cur_frm.fields_dict["electrical_bom_raw_material"].grid.add_custom_button(__('From Template'),
			function() {
	        table_name = "electrical_bom_raw_material"

	        cur_frm.trigger("item_templates")
        }).css('background-color','brown').css('color','white')

        //MECHANICAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL
	    cur_frm.fields_dict["mechanical_bom_raw_material"].grid.add_custom_button(__('Refresh Available Stock'),
			function() {
            cur_frm.trigger("refresh_mechanical_available_stock")
        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px')

	    cur_frm.fields_dict["mechanical_bom_raw_material"].grid.add_custom_button(__('Generate Item Template'),
			function() {
	        table_name = "mechanical_bom_raw_material"
	        cur_frm.trigger("generate_item_template")
        }).css('background-color','#CCCC00').css('margin-left','10px')

        cur_frm.fields_dict["mechanical_bom_raw_material"].grid.add_custom_button(__('From Template'),
			function() {
            table_name = "mechanical_bom_raw_material"
	        cur_frm.trigger("item_templates")
        }).css('background-color','brown').css('color','white')

        //ENCLOSUUUUUUUUUURE
	    cur_frm.fields_dict["fg_sellable_bom_raw_material"].grid.add_custom_button(__('Refresh Available Stock'),
			function() {
	        	        cur_frm.trigger("refresh_fg_sellable_available_stock")

        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px')


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
        cur_frm.call({
                doc: cur_frm.doc,
                method: 'check_sales_order',
                args: {},
                freeze: true,
                freeze_message: "Checking Sales Order...",
                async:false,
                callback: (r) => {
                    has_so= r.message
                }
            })

	        frappe.db.get_single_value("Manufacturing Settings","default_workstation")
                .then(d_workstation => {
                    workstation = d_workstation
                    frappe.db.get_doc('Workstation', d_workstation)
                        .then(doc => {
                            net_hour_rate = doc.hour_rate
                        })
            })
            frappe.db.get_single_value("Manufacturing Settings","default_operation")
                .then(d_operation => {
                    electrical_operation = d_operation

            })
            frappe.db.get_single_value("Manufacturing Settings","mechanical_bom_default_operation")
                .then(d_operation => {
                    mechanical_operation = d_operation

            })

            frappe.db.get_single_value("Manufacturing Settings","default_routing")
                .then(d_routing => {
                    routing = d_routing

            })
        frappe.db.get_single_value("Manufacturing Settings","default_raw_material_warehouse")
                .then(warehouse => {
                    raw_material_warehouse = warehouse

            })
        frappe.db.get_single_value("Manufacturing Settings","enclosure_default_operation")
                .then(d_operation => {
                    fg_sellable_operation = d_operation

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


        } else if(cur_frm.doc.docstatus && cur_frm.doc.status === "Rejected"){

                frm.add_custom_button(__("Create BOM"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'create_bom',
                        args: {},
                        freeze: true,
                        freeze_message: "Creating BOM...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                })

        }  else if(cur_frm.doc.docstatus && cur_frm.doc.status === "To Purchase Order" && has_so){

                frm.add_custom_button(__("Material Request"), () => {
                    cur_frm.trigger("material_request")
                })

        }
        if(cur_frm.doc.docstatus){
            cur_frm.set_df_property("electrical_bom_raw_material", "read_only", !cur_frm.doc.quotation_amended)
            cur_frm.set_df_property("mechanical_bom_raw_material", "read_only", !cur_frm.doc.quotation_amended)
            cur_frm.set_df_property("fg_sellable_bom_raw_material", "read_only", !cur_frm.doc.quotation_amended)
            var fields = ["item_code","item_name","qty","valuation_rate","rate","amount","available_qty", "discount", "uom", "batch", "warehouse"]
            for(var x=0;x<fields.length;x+=1){
                console.log(fields[x])
                var field = frappe.meta.get_docfield("Budget BOM Raw Material", fields[x], cur_frm.doc.name);
                field.read_only = !cur_frm.doc.quotation_amended
            }
        }


    },
	onload_post_render: function(frm) {
	    if(cur_frm.is_new()){

            cur_frm.add_child("electrical_bom_details", {
                workstation: workstation,
                operation: electrical_operation,
                qty: 1,
                net_hour_rate: net_hour_rate
            })
            cur_frm.add_child("mechanical_bom_details", {
                workstation:workstation,
                operation: mechanical_operation,
                qty: 1,
                net_hour_rate: net_hour_rate
            })
            cur_frm.add_child("fg_sellable_bom_details", {
                workstation: workstation,
                routing:routing,
                operation:fg_sellable_operation,
                qty: 1,
                net_hour_rate: net_hour_rate
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

compute_total_operation_cost(cur_frm)
            compute_total_cost_expense(cur_frm)
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
    total_additional_operation_cost: function(frm) {
        compute_total_cost_expense(cur_frm)
	},
    discount_amount: function(frm) {
        compute_total_cost_expense(cur_frm)
	},
    discount_percentage: function(frm) {
	    cur_frm.doc.discount_amount = (cur_frm.doc.discount_percentage / 100) * cur_frm.doc.total_raw_material_cost
        cur_frm.refresh_field("discount_amount")
        compute_total_cost_expense(cur_frm)
	},
    margin_: function(frm) {
        compute_total_cost_expense(cur_frm)
	},
    material_request: function(frm) {
       frappe.model.open_mapped_doc({
			method: "load_controls.load_controls.doctype.budget_bom.budget_bom.make_mr",
			frm: cur_frm
		})
	},
});

cur_frm.cscript.refresh_electrical_available_stock = function () {
     frappe.call({
            method: "load_controls.load_controls.doctype.budget_bom.budget_bom.set_available_qty",
            args: {
                items: cur_frm.doc.electrical_bom_raw_material
            },
            callback: function (r) {
                var objIndex = 0
               for(var x=0;x<r.message.length;x+=1){
                    console.log("NAA")
                   objIndex = cur_frm.doc.electrical_bom_raw_material.findIndex(obj => obj.name === r.message[x]['name'])

                    cur_frm.doc.electrical_bom_raw_material[objIndex].available_qty = r.message[x]['available_qty']
                   cur_frm.refresh_field("electrical_bom_raw_material")
               }
            }
        })
}
cur_frm.cscript.refresh_mechanical_available_stock = function () {
     frappe.call({
            method: "load_controls.load_controls.doctype.budget_bom.budget_bom.set_available_qty",
            args: {
                items: cur_frm.doc.mechanical_bom_raw_material
            },
            callback: function (r) {
                var objIndex = 0
               for(var x=0;x<r.message.length;x+=1){
                    console.log("NAA")
                   objIndex = cur_frm.doc.mechanical_bom_raw_material.findIndex(obj => obj.name === r.message[x]['name'])

                    cur_frm.doc.mechanical_bom_raw_material[objIndex].available_qty = r.message[x]['available_qty']
                   cur_frm.refresh_field("mechanical_bom_raw_material")
               }
            }
        })
}
cur_frm.cscript.refresh_fg_sellable_available_stock = function () {
     frappe.call({
            method: "load_controls.load_controls.doctype.budget_bom.budget_bom.set_available_qty",
            args: {
                items: cur_frm.doc.fg_sellable_bom_raw_material
            },
            callback: function (r) {
                var objIndex = 0
               for(var x=0;x<r.message.length;x+=1){
                    console.log("NAA")
                   objIndex = cur_frm.doc.fg_sellable_bom_raw_material.findIndex(obj => obj.name === r.message[x]['name'])

                    cur_frm.doc.fg_sellable_bom_raw_material[objIndex].available_qty = r.message[x]['available_qty']
                   cur_frm.refresh_field("fg_sellable_bom_raw_material")
               }
            }
        })
}
frappe.ui.form.on('Budget BOM Raw Material', {
    qty: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)


        if(d.amount > 0 && d.discount_percentage > 0){
            d.discount_amount = (d.discount_percentage / 100) * d.amount
            d.amount = d.amount - d.discount_amount
            cur_frm.refresh_field(d.parentfield)
        } else if (d.amount > 0 && d.discount_amount > 0){
             d.amount = d.amount - d.discount_amount
            cur_frm.refresh_field(d.parentfield)
        }

        compute_total_cost(cur_frm)
        compute_total_cost_expense(cur_frm)

	},
    rate: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)


        if(d.amount > 0 && d.discount_percentage > 0){
            d.discount_amount = (d.discount_percentage / 100) * d.amount
            d.amount = d.amount - d.discount_amount
            cur_frm.refresh_field(d.parentfield)
        } else if (d.amount > 0 && d.discount_amount > 0){
             d.amount = d.amount - d.discount_amount
            cur_frm.refresh_field(d.parentfield)
        }


        compute_total_cost(cur_frm)
        compute_total_cost_expense(cur_frm)

	},
    item_code: function (frm, cdt, cdn) {
         var d = locals[cdt][cdn]
        if(d.item_code){
            d.rate = get_rate(cur_frm, d).responseJSON.message[0]
            cur_frm.refresh_field(d.parentfield)
        }

    },
    discount_percentage: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(d.amount > 0 && d.discount_percentage > 0){
            d.discount_amount = (d.discount_percentage / 100) * d.amount
            d.amount = d.amount - d.discount_amount
            cur_frm.refresh_field(d.parentfield)

        }
         compute_total_cost(cur_frm)
        compute_total_cost_expense(cur_frm)

    },
    discount_amount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(d.amount > 0){
            d.amount = d.amount - d.discount_amount
            cur_frm.refresh_field(d.parentfield)
        }
         compute_total_cost(cur_frm)
        compute_total_cost_expense(cur_frm)

    }
});
frappe.ui.form.on('Additional Operational Cost', {
    amount: function(frm, cdt, cdn) {
        var total=0
       for(var ii=0;ii<cur_frm.doc.additional_operation_cost.length;ii+=1){
            total += cur_frm.doc.additional_operation_cost[ii].amount
        }
        cur_frm.doc.total_additional_operation_cost = total
        cur_frm.refresh_field("total_additional_operation_cost")
         compute_total_cost_expense(cur_frm)
	}
});
frappe.ui.form.on('Budget BOM Details', {
    workstation: function(frm, cdt, cdn) {
       compute_total_operation_cost(cur_frm)
        compute_total_cost_expense(cur_frm)
	}
});
function compute_total_cost_expense(cur_frm) {
    var total_cost = (cur_frm.doc.total_operation_cost + cur_frm.doc.total_additional_operation_cost + cur_frm.doc.total_raw_material_cost) - cur_frm.doc.discount_amount
   cur_frm.doc.total_cost = ( total_cost * (parseFloat(cur_frm.doc.margin_ ) / 100)) + total_cost
    cur_frm.refresh_field("total_cost")
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
function compute_total_operation_cost(cur_frm) {
    var fieldnames = ['electrical_bom_details','mechanical_bom_details','fg_sellable_bom_details']
    var total_hour_rate = 0
    for(var i=0;i<fieldnames.length;i+=1){
        if(cur_frm.doc[fieldnames[i]]){
            for(var ii=0;ii<cur_frm.doc[fieldnames[i]].length;ii+=1){
                total_hour_rate += parseFloat(cur_frm.doc[fieldnames[i]][ii].net_hour_rate)
            }
        }

    }
    console.log("TOTAL HOUR RATE")
    console.log(total_hour_rate)
    cur_frm.doc.total_operation_cost = total_hour_rate
    cur_frm.refresh_field("total_operation_cost")
}
function get_template(template_names, raw_material_table, cur_frm){
    for(var x=0;x<template_names.length;x+=1){
        console.log(template_names[x])
         frappe.db.get_doc("BOM Item Template", template_names[x])
            .then(doc => {
                for(var x=0;x<doc.items.length;x+=1){
                    var rate = get_rate(cur_frm, doc.items[x])
                    cur_frm.add_child(raw_material_table, {
                        item_code: doc.items[x].item_code,
                        item_name: doc.items[x].item_name,
                        uom: doc.items[x].uom,
                        qty: doc.items[x].qty,
                        rate: rate.responseJSON.message[0]
                    })
                    cur_frm.refresh_field(raw_material_table)
                }

        })
    }
}

function get_rate(cur_frm, d) {
    if(d.item_code){
        return frappe.call({
            method: "load_controls.load_controls.doctype.budget_bom.budget_bom.get_rate",
            args: {
                item_code: d.item_code,
                warehouse: d.warehouse ? d.warehouse : "",
                based_on: cur_frm.doc.rate_of_materials_based_on ? cur_frm.doc.rate_of_materials_based_on : "",
                price_list: cur_frm.doc.price_list ? cur_frm.doc.price_list : ""

            },
            async: false,
            callback: function (r) {
                console.log("RAAAAAAAAAAAAAAATE")
                console.log(r.message[0])
                return r.message[0]
            }
        })
    }

}

cur_frm.cscript.electrical_bom_raw_material_add = function (frm, cdt,cdn) {
    var d = locals[cdt][cdn]
    d.warehouse = raw_material_warehouse
    d.schedule_date = cur_frm.doc.posting_date
    cur_frm.refresh_field(d.parentfield)
}
cur_frm.cscript.mechanical_bom_raw_material_add = function (frm, cdt,cdn) {
    var d = locals[cdt][cdn]
    d.warehouse = raw_material_warehouse
    d.schedule_date = cur_frm.doc.posting_date
    cur_frm.refresh_field(d.parentfield)

}
cur_frm.cscript.fg_sellable_bom_raw_material_add = function (frm, cdt,cdn) {
    var d = locals[cdt][cdn]
    d.warehouse = raw_material_warehouse
    d.schedule_date = cur_frm.doc.posting_date
    cur_frm.refresh_field(d.parentfield)

}