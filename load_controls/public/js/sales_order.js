frappe.ui.form.on("Sales Order", {
    generate_project_code: function () {
        frappe.call({
                method: 'load_controls.doc_events.sales_order.generate_cost_centers',
                args: {
                    items: cur_frm.doc.items,
                    name: cur_frm.doc.name,
                    customer: cur_frm.doc.customer,
                    project_code: cur_frm.doc.cost_center ? cur_frm.doc.cost_center : "",
                    company: cur_frm.doc.company,
                },
                freeze: true,
                freeze_message: "Get Templates...",
                async: false,
                callback: (r) => {
                    cur_frm.reload_doc()
                }
        })
    },
    onload_post_render: function (frm) {
			 cur_frm.remove_custom_button("Work Order", "Create")
			 cur_frm.remove_custom_button("Pick List", "Create")
			 cur_frm.remove_custom_button("Material Request", "Create")
			 cur_frm.remove_custom_button("Request for Raw Materials", "Create")
			 cur_frm.remove_custom_button("Purchase Order", "Create")
			 cur_frm.remove_custom_button("Project", "Create")
			 cur_frm.remove_custom_button("Subscription", "Create")
	},
    refresh: function (frm) {
    	 cur_frm.remove_custom_button("Work Order", "Create")
			 cur_frm.remove_custom_button("Pick List", "Create")
			 cur_frm.remove_custom_button("Material Request", "Create")
			 cur_frm.remove_custom_button("Request for Raw Materials", "Create")
			 cur_frm.remove_custom_button("Purchase Order", "Create")
			 cur_frm.remove_custom_button("Project", "Create")
			 cur_frm.remove_custom_button("Subscription", "Create")
        document.querySelectorAll("[data-fieldname='generate_project_code']")[1].style.backgroundColor =" #80bfff"
       document.querySelectorAll("[data-fieldname='generate_project_code']")[1].style.color ="white"
       document.querySelectorAll("[data-fieldname='generate_project_code']")[1].style.fontWeight ="bold"

        if(cur_frm.doc.docstatus) {
             cur_frm.remove_custom_button("Work Order", "Create")
            cur_frm.add_custom_button(__('Custom Work Order'), () => cur_frm.trigger("make_work_order_bb"), __('Create'));

            cur_frm.add_custom_button('Material Request', () => {
                let query_args = {
                    query: "load_controls.doc_events.sales_order.get_budget_bom",
                    filters: {parent: cur_frm.doc.name}
                }
                new frappe.ui.form.MultiSelectDialog({
                    setters: {},
                    doctype: "Budget BOM",
                    target: cur_frm,
                    date_field: "posting_date",
                    get_query(){
                        return query_args;
                    },
                    action(selections) {
                        frappe.call({
                            method: "load_controls.doc_events.sales_order.generate_mr",
                            args: {
                                budget_boms: selections,
                                schedule_date: cur_frm.doc.delivery_date,
                                transaction_date: cur_frm.doc.transaction_date,
                                so_name: cur_frm.doc.name
                            },
                            async:false,
                            callback: function (r) {
                                 frappe.set_route("Form", "Material Request", r.message);
                            }
                        })
                    }
                })
            }).css('background-color','#8B4513').css('color','white').css('font-weight','bold')
        }
    },
    make_work_order_bb: function() {
		var me = this;
		frappe.call({
			method: 'load_controls.doc_events.sales_order.get_work_order_items',
            args:{
			  so: cur_frm.doc.name
            },
			callback: function(r) {
				if(!r.message) {
					frappe.msgprint({
						title: __('Work Order not created'),
						message: __('No Items with Bill of Materials to Manufacture'),
						indicator: 'orange'
					});
					return;
				}
				else if(!r.message) {
					frappe.msgprint({
						title: __('Work Order not created'),
						message: __('Work Order already created for all items with BOM'),
						indicator: 'orange'
					});
					return;
				} else {
					const fields = [{
						label: 'Items',
						fieldtype: 'Table',
						fieldname: 'items',
						description: __('Select BOM and Qty for Production'),
						fields: [{
							fieldtype: 'Read Only',
							fieldname: 'item_code',
							label: __('Item Code'),
							in_list_view: 1
						}, {
							fieldtype: 'Link',
							fieldname: 'bom',
							options: 'BOM',
							reqd: 1,
							label: __('Select BOM'),
							in_list_view: 1,
							get_query: function (doc) {
								return { filters: { item: doc.item_code } };
							}
						}, {
							fieldtype: 'Float',
							fieldname: 'pending_qty',
                            read_only: 1,
							reqd: 1,
							label: __('Qty'),
							in_list_view: 1,

						}, {
							fieldtype: 'Data',
							fieldname: 'sales_order_item',
							reqd: 1,
							label: __('Sales Order Item'),
							hidden: 1
						}, {
							fieldtype: 'Data',
							fieldname: 'budget_bom',
							reqd: 1,
							label: __('Budget BOM'),
							hidden: 0
						}],
						data: r.message,
						get_data: () => {
							return r.message
						}
					}]
					var d = new frappe.ui.Dialog({
						title: __('Select Items to Manufacture'),
						fields: fields,
						primary_action: function() {

							var data = d.get_values();
							for(var x=0;x<data.items.length;x+=1){
								if(data.items[x].pending_qty > 1){
									frappe.throw("Qty should be 1")
								}
							}
							frappe.call({
								method: 'load_controls.doc_events.sales_order.make_work_orders',
								args: {
									items: data,
									company: cur_frm.doc.company,
									sales_order: cur_frm.docname,
									project: cur_frm.project
								},
								freeze: true,
								callback: function(r) {
									if(r.message) {
										frappe.msgprint({
											message: __('Work Orders Created: {0}', [r.message.map(function(d) {
													return repl('<a href="/app/work-order/%(name)s">%(name)s</a>', {name:d})
												}).join(', ')]),
											indicator: 'green'
										})
									}
									d.hide();
								}
							});
						},
						primary_action_label: __('Create')
					});
					d.show();
				}
			}
		});
	},
})