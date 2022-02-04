// Copyright (c) 2021, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Discount', {
    all_update_to_budget_bom: function (frm){
        frappe.call({
            method: 'load_controls.load_controls.doctype.discount.discount.update_budget_boms',
            args: {
                opportunity: cur_frm.doc.opportunity ? cur_frm.doc.opportunity : "",
                item_groups: cur_frm.doc.discount_details ? cur_frm.doc.discount_details : []
            },
            freeze: true,
            freeze_message: "Get Templates...",
            async:false,
            callback: function(r) {
                frappe.show_alert({
                    message: __('Budget BOMs Updated'),
                    indicator: 'green'
                }, 3);
            }
        })
    },
    fetch_item_groups: function (frm){
        cur_frm.call({
            doc: cur_frm.doc,
            method: 'fetch_item_groups',
            args: {
                opportunity: cur_frm.doc.opportunity ? cur_frm.doc.opportunity : "",
                item_groups: cur_frm.doc.discount_details ? cur_frm.doc.discount_details : []
            },
            freeze: true,
            freeze_message: "Get Templates...",
            async:false,
            callback: (r) => {
                for(var x=0;x<r.message.length;x+=1){
                    cur_frm.add_child("discount_details", {
                        item_group: r.message[x]
                    })
            cur_frm.refresh_field("discount_details")
                }
            }
        })
    },
	refresh: function(frm) {
        cur_frm.set_query("item_group", "discount_details", () => {
            var names = Array.from(cur_frm.doc.discount_details, x => "item_group" in x ? x.item_group:"")
            return {
                filters: [
                   ["is_group","=", 0],
                   ["name","not in", names],
                ]
            }
        })
         for(var x=0;x<document.querySelectorAll("[data-fieldname='update_to_budget_bom']").length;x+=1){
            if(document.querySelectorAll("[data-fieldname='update_to_budget_bom']")[x].className === 'btn btn-xs btn-default'){
                document.querySelectorAll("[data-fieldname='update_to_budget_bom']")[x].style.backgroundColor ="blue"
               document.querySelectorAll("[data-fieldname='update_to_budget_bom']")[x].style.color ="white"
               document.querySelectorAll("[data-fieldname='update_to_budget_bom']")[x].style.fontWeight ="bold"
            }
        }
	}
});
frappe.ui.form.on('Discount Details', {
	update_to_budget_bom: function(frm, cdt, cdn) {
	    var d = locals[cdt][cdn]
        frappe.call({
            method: "load_controls.load_controls.doctype.discount.discount.update_budget_bom",
            args:{
                d: d,
                opportunity: cur_frm.doc.opportunity ? cur_frm.doc.opportunity : ""
            },
            async: false,
            callback: function (r) {
                frappe.show_alert({
                    message: __('Budget BOM Updated'),
                    indicator: 'green'
                }, 3);
            }
        })
	}
});

