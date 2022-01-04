// Copyright (c) 2021, jan and contributors
// For license information, please see license.txt
var e_workstation = ""
var m_workstation = ""
var en_workstation = ""
var electrical_operation = ""
var mechanical_operation = ""
var fg_sellable_operation = ""
var routing = ""
var has_quotation = false
var has_so = false
var generating_quotation = false
var check_bom = false
var table_name = ""
var e_net_hour_rate = 0
var m_net_hour_rate = 0
var en_net_hour_rate = 0
var e_operation_time = 0
var m_operation_time = 0
var en_operation_time = 0
var raw_material_warehouse = 0
var allow_bb = 0
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
function get_rate_from_raw_material(item_code, parentfield, rate) {
    var field = parentfield === 'mechanical_bom_additiondeletion' ? "mechanical_bom_raw_material" : "electrical_bom_raw_material"
    if(cur_frm.doc[field]){
       for(var x=0;x < cur_frm.doc[field].length;x+=1){
        if(cur_frm.doc[field][x].item_code === item_code){
            return cur_frm.doc[field][x].discount_rate
        }
        }
    }

    return rate
}
frappe.ui.form.on('Budget BOM Raw Material Modifier', {
    item_code: function (frm,cdt,cdn) {
        var d = locals[cdt][cdn]
        if(d.item_code){
            var rate = get_rate_from_raw_material(d.item_code, d.parentfield, d.discount_rate)
            d.discount_rate = rate
            d.amount = rate * d.qty
            cur_frm.refresh_field(d.parentfield)
                        compute_total_cost(cur_frm)

        }
    },
    qty: function (frm,cdt,cdn) {
        var d = locals[cdt][cdn]
        if(d.item_code){
            var rate = get_rate_from_raw_material(d.item_code, d.parentfield, d.discount_rate)
            d.discount_rate = rate
            d.amount = rate * d.qty
            cur_frm.refresh_field(d.parentfield)
            compute_total_cost(cur_frm)
        }
    }
})
frappe.ui.form.on('Budget BOM', {
    material_overhead: function () {
      compute_total_operation_cost(cur_frm)
        compute_total_cost(cur_frm)
    },
    operation_overhead: function () {
      compute_total_operation_cost(cur_frm)
        compute_total_cost(cur_frm)
    },
    material_margin: function () {
      compute_total_operation_cost(cur_frm)
        compute_total_cost(cur_frm)
    },
    operation_margin: function () {
      compute_total_operation_cost(cur_frm)
        compute_total_cost(cur_frm)
    },
    save_or_submit: function () {
        console.log("test")
    },
	refresh: function(frm) {
        if(cur_frm.is_new()) {
	        console.log(cur_frm.doc.posting_date)
            var date = new Date(cur_frm.doc.posting_date);
            date.setDate(date.getDate() + 30);
            console.log(date)
            console.log(date.getFullYear())
            console.log(date.getMonth()+1 + "-" + date.getDate() + "-" + date.getFullYear())
            var new_date = new Date(date.getMonth()+1 + "-" + date.getDate() + "-" + date.getFullYear())
            console.log(new_date)
            console.log(new_date.getMonth()+1)
            console.log(new_date.getDate())
            console.log(new_date.getFullYear())

            cur_frm.doc.expected_closing_date = date.getFullYear() + "-" + date.getMonth() + 1 + "-" + date.getDate()
            // cur_frm.doc.expected_closing_date = "2021-12-31"
            cur_frm.doc.status = "Pending"
            cur_frm.refresh_fields(["status","expected_closing_date"])

        }
    if(cur_frm.is_new()) {
            cur_frm.doc.status = "To Quotation"
            cur_frm.refresh_field("status")
        }
    document.querySelectorAll("[data-fieldname='update_discount']")[1].style.backgroundColor ="blue"
       document.querySelectorAll("[data-fieldname='update_discount']")[1].style.color ="white"
       document.querySelectorAll("[data-fieldname='update_discount']")[1].style.fontWeight ="bold"

	    cur_frm.set_query("opportunity", () => {
	        return {
	            filters:{
	                status: 'Open'
                }
            }
        })
        // cur_frm.set_query("item_code","mechanical_bom_additiondeletion", () => {
        //    var names = Array.from(cur_frm.doc.mechanical_bom_raw_material, x => "item_code" in x ? x.item_code:"")
        //    var names2 = Array.from(cur_frm.doc.mechanical_bom_additiondeletion, x => "item_code" in x ? x.item_code:"")
	     //    return {
	     //        filters:[
	     //            ["name", "in",names],
        //             ["name", "not in", names2]
        //         ]
        //     }
        // })
        // cur_frm.set_query("item_code","electrical_bom_additiondeletion", () => {
        //    var names = Array.from(cur_frm.doc.mechanical_bom_raw_material, x => "item_code" in x ? x.item_code:"")
        //    var names2 = Array.from(cur_frm.doc.mechanical_bom_additiondeletion, x => "item_code" in x ? x.item_code:"")
	     //    return {
	     //        filters:[
	     //            ["name", "in",names],
        //             ["name", "not in", names2]
        //         ]
        //     }
        // })
	    //ELECTRICAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL
	    cur_frm.fields_dict["electrical_bom_raw_material"].grid.add_custom_button(__('Refresh Available Stock'),
			function() {
	        cur_frm.trigger("refresh_electrical_available_stock")
        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px').css('font-weight','bold')

	    cur_frm.fields_dict["electrical_bom_raw_material"].grid.add_custom_button(__('Generate Item Template'),
			function() {
	        table_name = "electrical_bom_raw_material"
	        cur_frm.trigger("generate_item_template")
        }).css('background-color','#CCCC00').css('margin-left','10px').css('font-weight','bold')

        cur_frm.fields_dict["electrical_bom_raw_material"].grid.add_custom_button(__('From Template'),
			function() {
	        table_name = "electrical_bom_raw_material"

	        cur_frm.trigger("item_templates")
        }).css('background-color','brown').css('color','white').css('font-weight','bold')

        //MECHANICAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL
	    cur_frm.fields_dict["mechanical_bom_raw_material"].grid.add_custom_button(__('Refresh Available Stock'),
			function() {
            cur_frm.trigger("refresh_mechanical_available_stock")
        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px').css('font-weight','bold')

	    cur_frm.fields_dict["mechanical_bom_raw_material"].grid.add_custom_button(__('Generate Item Template'),
			function() {
	        table_name = "mechanical_bom_raw_material"
	        cur_frm.trigger("generate_item_template")
        }).css('background-color','#CCCC00').css('margin-left','10px').css('font-weight','bold')

        cur_frm.fields_dict["mechanical_bom_raw_material"].grid.add_custom_button(__('From Template'),
			function() {
            table_name = "mechanical_bom_raw_material"
	        cur_frm.trigger("item_templates")
        }).css('background-color','brown').css('color','white').css('font-weight','bold')

        //ENCLOSUUUUUUUUUURE
	    cur_frm.fields_dict["fg_sellable_bom_raw_material"].grid.add_custom_button(__('Refresh Available Stock'),
			function() {
	        	        cur_frm.trigger("refresh_fg_sellable_available_stock")

        }).css('background-color','#00008B').css('color','white').css('margin-left','10px').css('margin-right','10px').css('font-weight','bold')


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
        cur_frm.call({
                doc: cur_frm.doc,
                method: 'check_bom',
                args: {},
                freeze: true,
                freeze_message: "Checking Sales Order...",
                async:false,
                callback: (r) => {
                    check_bom= r.message
                }
            })
            frappe.db.get_single_value("Manufacturing Settings","allow_budget_bom_total_raw_material_cost")
                .then(allow => {
                            allow_bb = allow
            })
	        frappe.db.get_single_value("Manufacturing Settings","default_workstation")
                .then(d_workstation => {
                    e_workstation = d_workstation
                if(d_workstation){
                    frappe.db.get_doc('Workstation', d_workstation)
                        .then(doc => {
                            e_net_hour_rate = doc.hour_rate
                        })
                }

            })
          frappe.db.get_single_value("Manufacturing Settings","mechanical_bom_default_workstation")
                .then(d_workstation => {
                    m_workstation = d_workstation
              if(d_workstation){
                    frappe.db.get_doc('Workstation', d_workstation)
                        .then(doc => {
                            m_net_hour_rate = doc.hour_rate
                        })
              }

            })
         frappe.db.get_single_value("Manufacturing Settings","encluser_default_workstation")
                .then(d_workstation => {
                    en_workstation = d_workstation
                if(d_workstation){
                frappe.db.get_doc('Workstation', d_workstation)
                        .then(doc => {
                            en_net_hour_rate = doc.hour_rate
                        })
                }

            })
            frappe.db.get_single_value("Manufacturing Settings","default_operation")
                .then(d_operation => {
                    electrical_operation = d_operation

            })
            frappe.db.get_single_value("Manufacturing Settings","mechanical_bom_default_operation")
                .then(d_operation => {
                    mechanical_operation = d_operation

            })
            frappe.db.get_single_value("Manufacturing Settings","default_raw_material_warehouse")
                .then(warehouse => {
                    raw_material_warehouse = warehouse

            })
            frappe.db.get_single_value("Manufacturing Settings","enclosure_default_operation")
                .then(d_operation => {
                    fg_sellable_operation = d_operation

            })

          frappe.db.get_single_value("Manufacturing Settings","electrical_operation_time_in_minute")
                .then(minute => {
                    e_operation_time = minute

            })
          frappe.db.get_single_value("Manufacturing Settings","mechanical_operation_time_in_minute")
                .then(minute => {
                    m_operation_time = minute

            })
          frappe.db.get_single_value("Manufacturing Settings","enclosure_time_in_minute")
                .then(minute => {
                    en_operation_time = minute

            })

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
        } else if(cur_frm.doc.docstatus && cur_frm.doc.status === "To Design" ){
            // if(frappe.user.has_role("Sales User")) {
            //     frm.add_custom_button(__("Amend Quotation"), () => {
            //         cur_frm.call({
            //             doc: cur_frm.doc,
            //             method: 'amend_quotation',
            //             args: {},
            //             freeze: true,
            //             freeze_message: "Amending Quotation...",
            //             callback: (r) => {
            //                 cur_frm.reload_doc()
            //             }
            //         })
            //     })
            // }
            if(frappe.user.has_role("Mechanical")){
	                 frm.add_custom_button(__("Submit"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'action_to_design',
                        args: {
                            status: "To Material Request"
                        },
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }, "Action")
            frm.add_custom_button(__("Update Changes"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'action_to_design',
                        args: {
                            status: "Updated Changes"
                        },
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }, "Action")
            }



        } else if(cur_frm.doc.docstatus && cur_frm.doc.status === "Updated Changes" && cur_frm.doc.total_raw_material_cost < allow_bb){
            if(frappe.user.has_role("Sales User")) {
            frm.add_custom_button(__("Approve"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'action_to_design',
                        args: {
                            status: "To Material Request",
                        },
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }, "Action")
            frm.add_custom_button(__("Decline"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'action_to_design',
                        args: {
                            status: "To Material Request"
                        },
                        freeze: true,
                        freeze_message: "Amending Quotation...",
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }, "Action")
                }



        }  else if(cur_frm.doc.docstatus && cur_frm.doc.status === "To Material Request" ){

                frm.add_custom_button(__("Material Request"), () => {
                    cur_frm.trigger("material_request")
                })
        } else if(cur_frm.doc.docstatus && ["To Material Request", "To SO", "To PO", "To PO and SO"].includes(cur_frm.doc.status)){

              if(!check_bom) {
                    frm.add_custom_button(__("Create BOM"), () => {
                        cur_frm.call({
                            doc: cur_frm.doc,
                            method: 'create_bom',
                            args: {},
                            freeze: true,
                            freeze_message: "Creating BOM...",
                            callback: (r) => {
                                cur_frm.reload_doc()
                                frappe.show_alert({
                                    message: __('BOMs Created'),
                                    indicator: 'green'
                                }, 3);
                            }
                        })
                    })
                }

        }
         if(cur_frm.doc.docstatus && frappe.user.has_role("Sales User") && !(cur_frm.doc.status === "Updated Changes")) {
             cur_frm.set_df_property("electrical_bom_raw_material", "read_only", (!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))
             cur_frm.set_df_property("fg_sellable_raw_material", "read_only", (!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))
             cur_frm.set_df_property("mechanical_bom_raw_material", "read_only",  (!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))
             cur_frm.set_df_property("additional_operation_cost", "read_only",  (!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))

             var fields_for_cancel1 = [
                 "electrical_bom_raw_material",
                 "mechanical_bom_raw_material",
                 "fg_sellable_bom_raw_material",
                 "additional_operation_cost",
                 "posting_date",
                 "expected_closing_date",
                 "discount_percentage",
                 "discount_amount",
                 "rate_of_materials_based_on",
                 "price_list",
             ]

             for (var ii = 0; ii < fields_for_cancel1.length; ii += 1) {
                 cur_frm.set_df_property(fields_for_cancel1[ii], "read_only",(!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))
             }
         } else if(cur_frm.doc.docstatus && frappe.user.has_role("Mechanical") && cur_frm.doc.status === "Updated Changes") {

             cur_frm.set_df_property("electrical_bom_raw_material", "read_only", (!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))
             cur_frm.set_df_property("fg_sellable_raw_material", "read_only", (!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))
             cur_frm.set_df_property("mechanical_bom_raw_material", "read_only",  (!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))
             cur_frm.set_df_property("additional_operation_cost", "read_only",  (!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))

             var fields_for_cancel = [
                 "electrical_bom_raw_material",
                 "electrical_bom_details",
                 "mechanical_bom_raw_material",
                 "mechanical_bom_details",
                 "fg_sellable_bom_details",
                 "fg_sellable_bom_raw_material",
                 "additional_operation_cost",
                 "posting_date",
                 "expected_closing_date",
                 "discount_percentage",
                 "discount_amount",
                 "rate_of_materials_based_on",
                 "price_list",
             ]

             for (var ii = 0; ii < fields_for_cancel.length; ii += 1) {
                 cur_frm.set_df_property(fields_for_cancel[ii], "read_only",(!cur_frm.doc.quotation_cancelled && !cur_frm.doc.quotation_amended))
             }
         }
      var label_change = frappe.meta.get_docfield("Budget BOM Details","rate", cur_frm.doc.name);
        if(label_change){
            label_change.label = 'Child Qty'
            cur_frm.refresh_field("activity_details")
        }

    },

	onload_post_render: function(frm) {
	    if(cur_frm.is_new()){
	        cur_frm.doc.status = "To Quotation"
            cur_frm.refresh_field(status)
            if(cur_frm.doc.electrical_bom_details.length === 0){
                cur_frm.add_child("electrical_bom_details", {
                    workstation: e_workstation,
                    operation: electrical_operation,
                    qty: 1,
                    net_hour_rate: e_net_hour_rate,
                    operation_time_in_minutes: e_operation_time
                })
            }
            if(cur_frm.doc.mechanical_bom_details.length === 0){
                cur_frm.add_child("mechanical_bom_details", {
                    workstation:m_workstation,
                    operation: mechanical_operation,
                    qty: 1,
                    net_hour_rate: m_net_hour_rate,
                    operation_time_in_minutes: m_operation_time
                })
            }
            if(cur_frm.doc.fg_sellable_bom_details.length === 0){
                cur_frm.add_child("fg_sellable_bom_details", {
                    workstation: en_workstation,
                    operation:fg_sellable_operation,
                    qty: 1,
                    net_hour_rate: en_net_hour_rate,
                    operation_time_in_minutes: en_operation_time
                })
            }




            compute_total_operation_cost(cur_frm)
             compute_total_cost(cur_frm)
        }
cur_frm.get_field("electrical_bom_details").grid.cannot_add_rows = true;
            cur_frm.get_field("mechanical_bom_details").grid.cannot_add_rows = true;
            cur_frm.get_field("fg_sellable_bom_details").grid.cannot_add_rows = true;

            cur_frm.refresh_field("electrical_bom_details")
            cur_frm.refresh_field("mechanical_bom_details")
            cur_frm.refresh_field("fg_sellable_bom_details")

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


        if(d.rate > 0 && d.discount_percentage > 0){
            d.discount_rate = (d.rate * (1 - (d.discount_percentage / 100)))
            d.discount_amount = (d.discount_percentage / 100) * d.rate
            d.amount = d.qty * d.discount_rate
            cur_frm.refresh_field(d.parentfield)
        }else if (d.rate > 0 && d.discount_amount > 0){
            d.discount_rate = d.rate - d.discount_amount
            d.amount = d.qty * d.discount_rate
            cur_frm.refresh_field(d.parentfield)
        } else {
            d.discount_rate = d.rate
            cur_frm.refresh_field(d.parentfield)
        }

        if(d.parentfield === 'fg_sellable_bom_raw_material'){
         d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
        }
        compute_total_cost(cur_frm)

	},
    rate: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)


        if(d.rate > 0 && d.discount_percentage > 0){
            d.discount_rate = (d.rate * (1 - (d.discount_percentage / 100)))
            d.discount_amount = (d.discount_percentage / 100) * d.rate
            d.amount = d.qty * d.discount_rate
            cur_frm.refresh_field(d.parentfield)
        } else if (d.rate > 0 && d.discount_amount > 0){
            d.discount_rate = d.rate - d.discount_amount
            d.amount = d.qty * d.discount_rate
            cur_frm.refresh_field(d.parentfield)
        } else {
            d.discount_rate = d.rate
            cur_frm.refresh_field(d.parentfield)
        }
            if(d.parentfield === 'fg_sellable_bom_raw_material'){
                d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
            }
        compute_total_cost(cur_frm)

	},
    item_code: function (frm, cdt, cdn) {
         var d = locals[cdt][cdn]
        if(d.item_code){

            var fieldname = d.parentfield === "electrical_bom_raw_material" ? "refresh_electrical_available_stock" :
                            d.parentfield === "mechanical_bom_raw_material" ? "refresh_mechanical_available_stock" :
                                d.parentfield === "fg_sellable_bom_raw_material" ? "refresh_fg_sellable_available_stock" : ""
            if(fieldname){
                            cur_frm.trigger(fieldname)

            }
             cur_frm.call({
                doc: cur_frm.doc,
                method: 'get_discount',
                args: {
                    item: d,
                    raw_material_table: fieldname
                },
                freeze: true,
                freeze_message: "Get Templates...",
                async:false,
                callback: (r) => {
                    console.log("ITEM CODEEEE TRIGGER")
                    console.log(r.message.discount_rate)
                        var values = r.message
                                console.log(values.discount_rate)
                            d.item_name = values.item_name
                            d.discount_rate = values.discount_rate > 0 ? values.discount_rate : values.amount
                          d.link_discount_amount = values.link_discount_amount
                          d.discount_amount = values.discount_amount ? values.discount_amount : 0
                          d.discount_percentage = values.discount_percentage ? values.discount_percentage : 0
                          d.rate = values.rate
                          d.amount = values.amount
                            cur_frm.refresh_field(d.parentfield)
                 }
            })
        compute_total_cost(cur_frm)
        }

    },
    discount_percentage: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
         d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)

      if(d.rate > 0){
        d.discount_rate = (d.rate * (1 - (d.discount_percentage / 100)))
       d.discount_amount = (d.discount_percentage / 100) * d.rate
        d.amount = d.qty * d.discount_rate
        cur_frm.refresh_field(d.parentfield)
    }

            if(d.parentfield === 'fg_sellable_bom_raw_material'){
             d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
            }

         compute_total_cost(cur_frm)


    },
    discount_amount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
         d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)
          if (d.rate > 0){
                        d.discount_rate = d.rate - d.discount_amount
                        d.amount = d.stock_qty * d.discount_rate
                        cur_frm.refresh_field(d.parentfield)
                    }



        compute_total_cost(cur_frm)

    },
    unlink_discount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(cur_frm.doc.docstatus){
            frappe.call({
                method: "ringlus.ringlus.doctype.budget_bom.budget_bom.unlink",
                args: {
                    name: d.name
                },
                async: false,
                callback: function (r) {
                    cur_frm.reload_doc()
                }
            })
        } else{
            d.link_discount_amount = ""
            cur_frm.refresh_field(d.parentfield)
        }
    },
   save_discount_amount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(d.discount_percentage > 0 && d.item_code){
             cur_frm.call({
                doc: cur_frm.doc,
                method: 'add_or_save_discount',
                args: {
                    opportunity: cur_frm.doc.opportunity,
                    item_group: d.item_group,
                    discount_percentage: d.discount_percentage,
                    remarks: d.remarks ? d.remarks : '',
                },
                freeze: true,
                freeze_message: "Discount...",
                async:false,
                callback: (r) => {
                        frappe.show_alert({
                            message:__('Discount created or updated'),
                            indicator:'green'
                        }, 3);
                        d.link_discount_amount = r.message
                        cur_frm.refresh_field(d.parentfield)
                }
            })

        }



    },
    update_discount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(d.item_group){
            cur_frm.call({
                doc: cur_frm.doc,
                method: 'update_discount',
                args: {
                    item: d
                },
                freeze: true,
                freeze_message: "Get Templates...",
                async:false,
                callback: (r) => {
                    console.log("ITEM CODEEEE TRIGGER")
                    console.log(r.message.discount_rate)
                        var values = r.message
                            console.log(values.discount_rate)

                            d.discount_rate = values.discount_rate > 0 ? values.discount_rate : values.amount
                          d.link_discount_amount = values.link_discount_amount
                          d.discount_amount = values.discount_amount
                          d.discount_percentage = values.discount_percentage
                          d.rate = values.rate
                          d.amount = values.amount
                            cur_frm.refresh_field(d.parentfield)

                 }
            })
        }
    },
    kg: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
        cur_frm.refresh_field(d.parentfield)

        compute_total_cost(cur_frm)
    },
    per_kg: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
        cur_frm.refresh_field(d.parentfield)

        compute_total_cost(cur_frm)
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
        compute_total_cost(cur_frm)
	},
    additional_operation_cost_remove: function () {
         var total=0
       for(var ii=0;ii<cur_frm.doc.additional_operation_cost.length;ii+=1){
            total += cur_frm.doc.additional_operation_cost[ii].amount
        }
        cur_frm.doc.total_additional_operation_cost = total
        cur_frm.refresh_field("total_additional_operation_cost")
        compute_total_cost(cur_frm)
    }
});
frappe.ui.form.on('Budget BOM Enclosure Raw Material', {
    qty: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)


        if(d.rate > 0 && d.discount_percentage > 0){
            d.discount_rate = (d.rate * (1 - (d.discount_percentage / 100)))
            d.discount_amount = (d.discount_percentage / 100) * d.rate
            d.amount = d.qty * d.discount_rate
            cur_frm.refresh_field(d.parentfield)
        }else if (d.rate > 0 && d.discount_amount > 0){
            d.discount_rate = d.rate - d.discount_amount
            d.amount = d.qty * d.discount_rate
            cur_frm.refresh_field(d.parentfield)
        } else {
            d.discount_rate = d.rate
            cur_frm.refresh_field(d.parentfield)
        }

        if(d.parentfield === 'fg_sellable_bom_raw_material'){
         d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
        }
        compute_total_cost(cur_frm)

	},
    rate: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)


        if(d.rate > 0 && d.discount_percentage > 0){
            d.discount_rate = (d.rate * (1 - (d.discount_percentage / 100)))
            d.discount_amount = (d.discount_percentage / 100) * d.rate
            d.amount = d.qty * d.discount_rate
            cur_frm.refresh_field(d.parentfield)
        } else if (d.rate > 0 && d.discount_amount > 0){
            d.discount_rate = d.rate - d.discount_amount
            d.amount = d.qty * d.discount_rate
            cur_frm.refresh_field(d.parentfield)
        } else {
            d.discount_rate = d.rate
            cur_frm.refresh_field(d.parentfield)
        }
            if(d.parentfield === 'fg_sellable_bom_raw_material'){
                d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
            }
        compute_total_cost(cur_frm)

	},
    item_code: function (frm, cdt, cdn) {
         var d = locals[cdt][cdn]
        if(d.item_code){

            var fieldname = d.parentfield === "electrical_bom_raw_material" ? "refresh_electrical_available_stock" :
                            d.parentfield === "mechanical_bom_raw_material" ? "refresh_mechanical_available_stock" :
                                d.parentfield === "fg_sellable_bom_raw_material" ? "refresh_fg_sellable_available_stock" : ""
            if(fieldname){
                            cur_frm.trigger(fieldname)

            }
             cur_frm.call({
                doc: cur_frm.doc,
                method: 'get_discount',
                args: {
                    item: d,
                    raw_material_table: fieldname
                },
                freeze: true,
                freeze_message: "Get Templates...",
                async:false,
                callback: (r) => {
                    console.log("ITEM CODEEEE TRIGGER")
                    console.log(r.message.discount_rate)
                        var values = r.message
                                console.log(values.discount_rate)
                            d.item_name = values.item_name
                            d.discount_rate = values.discount_rate > 0 ? values.discount_rate : values.amount
                          d.link_discount_amount = values.link_discount_amount
                          d.discount_amount = values.discount_amount ? values.discount_amount : 0
                          d.discount_percentage = values.discount_percentage ? values.discount_percentage : 0
                          d.rate = values.rate
                          d.amount = values.amount
                            cur_frm.refresh_field(d.parentfield)
                 }
            })
        compute_total_cost(cur_frm)
        }

    },
    discount_percentage: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
         d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)

      if(d.rate > 0){
        d.discount_rate = (d.rate * (1 - (d.discount_percentage / 100)))
       d.discount_amount = (d.discount_percentage / 100) * d.rate
        d.amount = d.qty * d.discount_rate
        cur_frm.refresh_field(d.parentfield)
    }

            if(d.parentfield === 'fg_sellable_bom_raw_material'){
             d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
            }

         compute_total_cost(cur_frm)


    },
    discount_amount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
         d.amount = d.qty * d.rate
        cur_frm.refresh_field(d.parentfield)
          if (d.rate > 0){
                        d.discount_rate = d.rate - d.discount_amount
                        d.amount = d.stock_qty * d.discount_rate
                        cur_frm.refresh_field(d.parentfield)
                    }



        compute_total_cost(cur_frm)

    },
    unlink_discount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(cur_frm.doc.docstatus){
            frappe.call({
                method: "ringlus.ringlus.doctype.budget_bom.budget_bom.unlink",
                args: {
                    name: d.name
                },
                async: false,
                callback: function (r) {
                    cur_frm.reload_doc()
                }
            })
        } else{
            d.link_discount_amount = ""
            cur_frm.refresh_field(d.parentfield)
        }
    },
   save_discount_amount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(d.discount_percentage > 0 && d.item_code){
             cur_frm.call({
                doc: cur_frm.doc,
                method: 'add_or_save_discount',
                args: {
                    opportunity: cur_frm.doc.opportunity,
                    item_group: d.item_group,
                    discount_percentage: d.discount_percentage,
                    remarks: d.remarks ? d.remarks : '',
                },
                freeze: true,
                freeze_message: "Discount...",
                async:false,
                callback: (r) => {
                        frappe.show_alert({
                            message:__('Discount created or updated'),
                            indicator:'green'
                        }, 3);
                        d.link_discount_amount = r.message
                        cur_frm.refresh_field(d.parentfield)
                }
            })

        }



    },
    update_discount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if(d.item_group){
            cur_frm.call({
                doc: cur_frm.doc,
                method: 'update_discount',
                args: {
                    item: d
                },
                freeze: true,
                freeze_message: "Get Templates...",
                async:false,
                callback: (r) => {
                    console.log("ITEM CODEEEE TRIGGER")
                    console.log(r.message.discount_rate)
                        var values = r.message
                            console.log(values.discount_rate)

                            d.discount_rate = values.discount_rate > 0 ? values.discount_rate : values.amount
                          d.link_discount_amount = values.link_discount_amount
                          d.discount_amount = values.discount_amount
                          d.discount_percentage = values.discount_percentage
                          d.rate = values.rate
                          d.amount = values.amount
                            cur_frm.refresh_field(d.parentfield)

                 }
            })
        }
    },
    kg: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
        cur_frm.refresh_field(d.parentfield)

        compute_total_cost(cur_frm)
    },
    per_kg: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.amount = ((d.qty * d.discount_rate) - d.discount_amount) * d.kg
        cur_frm.refresh_field(d.parentfield)

        compute_total_cost(cur_frm)
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
        compute_total_cost(cur_frm)
	},
    additional_operation_cost_remove: function () {
         var total=0
       for(var ii=0;ii<cur_frm.doc.additional_operation_cost.length;ii+=1){
            total += cur_frm.doc.additional_operation_cost[ii].amount
        }
        cur_frm.doc.total_additional_operation_cost = total
        cur_frm.refresh_field("total_additional_operation_cost")
        compute_total_cost(cur_frm)
    }
});
frappe.ui.form.on('Budget BOM Details', {
    workstation: function(frm, cdt, cdn) {
       compute_total_operation_cost(cur_frm)
        compute_total_cost(cur_frm)
	}
});
function compute_total_cost(cur_frm) {
    var fieldnames = ['electrical_bom_raw_material','mechanical_bom_raw_material','fg_sellable_bom_raw_material', 'mechanical_bom_additiondeletion','electrical_bom_additiondeletion']
    var total = 0
    var enclosure_subtotal = 0
    for(var i=0;i<fieldnames.length;i+=1){
        if(cur_frm.doc[fieldnames[i]]){
            for(var ii=0;ii<cur_frm.doc[fieldnames[i]].length;ii+=1){
                total += cur_frm.doc[fieldnames[i]][ii].amount
                if(fieldnames[i] === 'fg_sellable_bom_raw_material'){
                    enclosure_subtotal += cur_frm.doc[fieldnames[i]][ii].amount
                }
            }
        }
    }
    cur_frm.doc.total_raw_material_cost = total
    cur_frm.doc.enclosure_subtotal = enclosure_subtotal
    cur_frm.refresh_fields(["total_raw_material_cost", "enclosure_subtotal"])
    compute_other_figures(cur_frm)
}
function compute_other_figures(cur_frm) {
    var item_row = cur_frm.doc
    item_row.material_overhead_amount = cur_frm.doc.total_raw_material_cost * (cur_frm.doc.material_overhead / 100)
    item_row.material_cost = item_row.total_raw_material_cost + (item_row.total_raw_material_cost * (item_row.material_overhead / 100 ))

    item_row.operation_overhead_amount = item_row.estimated_bom_operation_cost * (item_row.operation_overhead / 100 )
    item_row.operation_cost = item_row.estimated_bom_operation_cost + (item_row.estimated_bom_operation_cost * (item_row.operation_overhead / 100 ))

    item_row.material_margin_amount = (item_row.material_cost / (1 - (item_row.material_margin / 100 ))) - item_row.material_cost
    item_row.total_margin_cost = item_row.material_cost + item_row.material_margin_amount


    item_row.operation_margin_amount = (item_row.operation_cost / (1 - (item_row.operation_margin/ 100 ))) - item_row.operation_cost
    item_row.total_operation_cost = item_row.operation_cost + item_row.operation_margin_amount

    item_row.total_cost = item_row.total_margin_cost + item_row.total_operation_cost + item_row.total_additional_operation_cost
    cur_frm.refresh_fields([
        "material_overhead_amount", "material_cost",
        "operation_overhead_amount", "operation_cost",
        "material_margin_amount", "total_margin_cost",
        "operation_margin_amount", "total_operation_cost",
        "total_cost"
    ])

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
    cur_frm.doc.estimated_bom_operation_cost = total_hour_rate
    cur_frm.refresh_field("total_operation_cost")
}
function get_template(template_names, raw_material_table, cur_frm){
     cur_frm.call({
        doc: cur_frm.doc,
        method: 'get_templates',
        args: {
            templates: template_names,
            raw_material_table: raw_material_table
        },
        freeze: true,
        freeze_message: "Get Templates...",
        async:false,
        callback: (r) => {
            cur_frm.dirty()
             compute_total_cost(cur_frm)
         }
    })
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
cur_frm.cscript.electrical_bom_details_on_form_rendered = function (frm, cdt,cdn) {
   if(cur_frm.get_field("electrical_bom_details").grid.df.read_only){
        for(var i=0;i<cur_frm.doc.electrical_bom_details.length;i+=1){
            for(var x=0;x<frappe.meta.get_fieldnames("Budget BOM Details").length;x+=1) {
                cur_frm.get_field("electrical_bom_details").grid.grid_rows[i].toggle_editable(frappe.meta.get_fieldnames("Budget BOM Raw Material")[x], false)
            }

        }
    }

}
cur_frm.cscript.mechanical_bom_details_on_form_rendered = function (frm, cdt,cdn) {
   if(cur_frm.get_field("mechanical_bom_details").grid.df.read_only){
        for(var i=0;i<cur_frm.doc.mechanical_bom_details.length;i+=1){
            for(var x=0;x<frappe.meta.get_fieldnames("Budget BOM Details").length;x+=1) {
                cur_frm.get_field("mechanical_bom_details").grid.grid_rows[i].toggle_editable(frappe.meta.get_fieldnames("Budget BOM Raw Material")[x], false)
            }

        }
    }

}
cur_frm.cscript.fg_sellable_bom_details_on_form_rendered = function (frm, cdt,cdn) {
   if(cur_frm.get_field("fg_sellable_bom_details").grid.df.read_only){
        for(var i=0;i<cur_frm.doc.fg_sellable_bom_details.length;i+=1){
            for(var x=0;x<frappe.meta.get_fieldnames("Budget BOM FG Details").length;x+=1) {
                cur_frm.get_field("fg_sellable_bom_details").grid.grid_rows[i].toggle_editable(frappe.meta.get_fieldnames("Budget BOM Raw Material")[x], false)
            }

        }
    }

}
cur_frm.cscript.electrical_bom_raw_material_on_form_rendered = function (frm, cdt,cdn) {

    for(var x=0;x<document.querySelectorAll("[data-fieldname='save_discount_amount']").length;x+=1){
        if(document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].className === 'btn btn-xs btn-default'){
            document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.backgroundColor ="blue"
           document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.color ="white"
           document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.fontWeight ="bold"
        }
    }
     for(var x=0;x<document.querySelectorAll("[data-fieldname='unlink_discount']").length;x+=1){
        if(document.querySelectorAll("[data-fieldname='unlink_discount']")[x].className === 'btn btn-xs btn-default'){
            document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.backgroundColor ="blue"
           document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.color ="white"
           document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.fontWeight ="bold"

        }
    }
     if(cur_frm.get_field("electrical_bom_raw_material").grid.df.read_only){
        for(var i=0;i<cur_frm.doc.electrical_bom_raw_material.length;i+=1){
            for(var x=0;x<frappe.meta.get_fieldnames("Budget BOM Raw Material").length;x+=1) {
                cur_frm.get_field("electrical_bom_raw_material").grid.grid_rows[i].toggle_editable(frappe.meta.get_fieldnames("Budget BOM Raw Material")[x], false)
            }

        }
    }
}
cur_frm.cscript.mechanical_bom_raw_material_on_form_rendered = function (frm, cdt,cdn) {
   for(var x=0;x<document.querySelectorAll("[data-fieldname='save_discount_amount']").length;x+=1){
        if(document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].className === 'btn btn-xs btn-default'){
            document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.backgroundColor ="blue"
           document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.color ="white"
           document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.fontWeight ="bold"

        }
    }
    for(var x=0;x<document.querySelectorAll("[data-fieldname='unlink_discount']").length;x+=1){
        if(document.querySelectorAll("[data-fieldname='unlink_discount']")[x].className === 'btn btn-xs btn-default'){
            document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.backgroundColor ="blue"
           document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.color ="white"
           document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.fontWeight ="bold"

        }
    }
     if(cur_frm.get_field("mechanical_bom_raw_material").grid.df.read_only){
        for(var i=0;i<cur_frm.doc.mechanical_bom_raw_material.length;i+=1){
            for(var x=0;x<frappe.meta.get_fieldnames("Budget BOM Raw Material").length;x+=1) {
                cur_frm.get_field("mechanical_bom_raw_material").grid.grid_rows[i].toggle_editable(frappe.meta.get_fieldnames("Budget BOM Raw Material")[x], false)
            }

        }
    }
}
cur_frm.cscript.fg_sellable_bom_raw_material_on_form_rendered = function (frm, cdt,cdn) {
    for(var x=0;x<document.querySelectorAll("[data-fieldname='save_discount_amount']").length;x+=1){
        if(document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].className === 'btn btn-xs btn-default'){
            document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.backgroundColor ="blue"
           document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.color ="white"
           document.querySelectorAll("[data-fieldname='save_discount_amount']")[x].style.fontWeight ="bold"
        }
    }
       for(var x=0;x<document.querySelectorAll("[data-fieldname='unlink_discount']").length;x+=1){
        if(document.querySelectorAll("[data-fieldname='unlink_discount']")[x].className === 'btn btn-xs btn-default'){
            document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.backgroundColor ="blue"
           document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.color ="white"
           document.querySelectorAll("[data-fieldname='unlink_discount']")[x].style.fontWeight ="bold"

        }
    }
    if(cur_frm.get_field("fg_sellable_bom_raw_material").grid.df.read_only){
        for(var i=0;i<cur_frm.doc.fg_sellable_bom_raw_material.length;i+=1){
            for(var x=0;x<frappe.meta.get_fieldnames("Budget BOM Raw Material").length;x+=1) {
                cur_frm.get_field("fg_sellable_bom_raw_material").grid.grid_rows[i].toggle_editable(frappe.meta.get_fieldnames("Budget BOM Raw Material")[x], false)
            }

        }
    }
}
cur_frm.cscript.additional_operation_cost_on_form_rendered = function (frm, cdt,cdn) {

if(cur_frm.get_field("additional_operation_cost").grid.df.read_only){
    for(var i=0;i<cur_frm.doc.additional_operation_cost.length;i+=1){
           cur_frm.get_field("additional_operation_cost").grid.grid_rows[i].toggle_editable("cost_type",false)
           cur_frm.get_field("additional_operation_cost").grid.grid_rows[i].toggle_editable("description",false)
           cur_frm.get_field("additional_operation_cost").grid.grid_rows[i].toggle_editable("amount",false)

    }
}

}