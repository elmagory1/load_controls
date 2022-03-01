from . import __version__ as app_version

app_name = "load_controls"
app_title = "Load Controls"
app_publisher = "jan"
app_description = "Load Controls"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "janlloydangeles@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/load_controls/css/load_controls.css"
# app_include_js = "/assets/load_controls/js/load_controls.js"

# include js, css files in header of web template
# web_include_css = "/assets/load_controls/css/load_controls.css"
# web_include_js = "/assets/load_controls/js/load_controls.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "load_controls/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Purchase Order" : "public/js/purchase_order.js",
	"Purchase Receipt" : "public/js/purchase_receipt.js",
	"Quotation" : "public/js/quotation.js",
	"Material Request" : "public/js/material_request.js",
	"Opportunity" : "public/js/opportunity.js",
	"Work Order" : "public/js/work_order.js",
	"Sales Order" : "public/js/sales_order.js",
	"Supplier Quotation" : "public/js/supplier_quotation.js",
	"Request for Quotation" : "public/js/request_for_quotation.js",
}
doctype_list_js = {
	"Quotation" : "public/js/quotation_list.js",
	"Opportunity" : "public/js/opportunity_list.js",
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "load_controls.install.before_install"
# after_install = "load_controls.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "load_controls.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Job Card": {
		"validate": "load_controls.doc_events.job_card.save_job_card",
	},
	"Quotation": {
		"on_submit": "load_controls.doc_events.quotation.submit_q",
		"validate": "load_controls.doc_events.quotation.validate_q",
		"on_cancel": "load_controls.doc_events.quotation.cancel_q",
	},
	"Material Request": {
		"on_submit": "load_controls.doc_events.utils.on_submit_record",
		"on_cancel": "load_controls.doc_events.material_request.on_cancel_mr",
		"on_trash": "load_controls.doc_events.utils.on_cancel_record",
		"validate": "load_controls.doc_events.material_request.validate_mr",
	},
	"Purchase Order": {
		"on_submit": "load_controls.doc_events.purchase_order.on_submit_po",
		"on_cancel": "load_controls.doc_events.purchase_order.on_cancel_po",
	},
	"Purchase Invoice": {
		"on_submit": "load_controls.doc_events.purchase_invoice.on_submit_pi",
		"on_cancel": "load_controls.doc_events.purchase_invoice.on_cancel_pi",
	},
	"Purchase Receipt": {
		"on_submit": "load_controls.doc_events.purchase_receipt.on_submit_pr",
		"on_cancel": "load_controls.doc_events.purchase_receipt.on_cancel_pr",
		"validate": "load_controls.doc_events.purchase_receipt.validate_pr",
	},
	"Sales Order": {
		"on_submit": "load_controls.doc_events.sales_order.on_submit_so",
		"on_cancel": "load_controls.doc_events.sales_order.on_cancel_so",
	},
	"Delivery Note": {
		"on_submit": "load_controls.doc_events.delivery_note.on_submit_dn",
		"on_cancel": "load_controls.doc_events.delivery_note.on_cancel_dn",
	},
	"Sales Invoice": {
		"on_submit": "load_controls.doc_events.sales_invoice.on_submit_si",
		"on_cancel": "load_controls.doc_events.sales_invoice.on_cancel_si",
	},
	"Supplier Quotation": {
		"on_submit": "load_controls.doc_events.supplier_quotation.on_submit_sq",
		"on_cancel": "load_controls.doc_events.supplier_quotation.on_cancel_sq",
	},
	"Stock Entry": {
		"on_submit": "load_controls.doc_events.stock_entry.on_submit_se",
		"validate": "load_controls.doc_events.stock_entry.on_save_se",
	},
	"Work Order": {
		"validate": "load_controls.doc_events.work_order.on_save_wo",
	},
	"Request for Quotation": {
		"on_submit": "load_controls.doc_events.request_for_quotation.on_submit_rfq",
		"on_cancel": "load_controls.doc_events.request_for_quotation.on_cancel_rfq",
	},
	"Pick List": {
		"on_submit": "load_controls.doc_events.pick_list.on_submit_pl",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"load_controls.tasks.all"
# 	],
# 	"daily": [
# 		"load_controls.tasks.daily"
# 	],
# 	"hourly": [
# 		"load_controls.tasks.hourly"
# 	],
# 	"weekly": [
# 		"load_controls.tasks.weekly"
# 	]
# 	"monthly": [
# 		"load_controls.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "load_controls.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "load_controls.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "load_controls.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"load_controls.auth.validate"
# ]
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Quotation-budget_bom",
                    "Quotation-reference",
                    "Quotation-budget_bom_reference",
                    "Quotation-opportunities",
                    "Quotation-budget_bom_opportunity",
                    "Quotation-additional_operating_cost",
                    "Sales Order-budget_bom_reference",
                    "Sales Order-reference",
                    "Sales Order-additional_operating_cost",
                    "BOM-budget_bom",
                    "Material Request Item-budget_bom_rate",
                    "Material Request-budget_bom",
                    "Purchase Order Item-budget_bom_rate",

                    "Manufacturing Settings-default_operation",
                    "Manufacturing Settings-mechanical_bom_default_operation",
                    "Manufacturing Settings-enclosure_default_operation",

                    "Manufacturing Settings-default_workstation",
                    "Manufacturing Settings-mechanical_bom_default_workstation",
                    "Manufacturing Settings-encluser_default_workstation",

                    "Manufacturing Settings-enclosure_time_in_minute",
                    "Manufacturing Settings-electrical_operation_time_in_minute",
                    "Manufacturing Settings-mechanical_operation_time_in_minute",

                    "Manufacturing Settings-cb1",
                    "Manufacturing Settings-cb2",
                    "Manufacturing Settings-budget_bom_defaults",

                    "Manufacturing Settings-default_raw_material_warehouse",


					"Manufacturing Settings-allow_budget_bom_total_raw_material_cost",
                    "Manufacturing Settings-allow_amount_budget_bom_without_approval",

                    "Purchase Order-approve_po_rate",
                    "Workstation-operation_time",
                    "Purchase Order-budget_bom",
                    "Purchase Invoice-budget_bom",
                    "Purchase Receipt-budget_bom",
                    "Sales Invoice-budget_bom_reference",
                    "Sales Invoice-references",
                    "Delivery Note-budget_bom_reference",
                    "Delivery Note-reference",
                    "BOM Item-operation_time_in_minutes",
                    "Material Request Item-budget_bom_raw_material",
                    "Purchase Invoice-budget_bom_reference",
                    "Purchase Invoice-reference",
                    "Purchase Receipt-reference",
                    "Purchase Receipt-budget_bom_reference",
					"Purchase Order-reference",
                    "Purchase Order-budget_bom_reference",
					"Material Request-reference_bom",
                    "Material Request-budget_bom_reference",
                    "Opportunity-project",
                    "Opportunity-budget_bom",

                    "Sales Order-cost_center",
                    "Sales Order-generate_project_code",
                    "Sales Order Item-references",
                    "Sales Order Item-project_code",
                    "Global Defaults-default_project_code",
                    "Supplier Quotation-fetch_material_request",
                    "Supplier Quotation Item-budget_bom_rate",

                    "Supplier Quotation-reference_bom",
                    "Supplier Quotation-budget_bom_reference",

                    "Operation-quality_inspection_required",
                    "Job Card-quality_inspection_required",
                    "Work Order-budget_bom_reference",
                    "Work Order-reference",
                    "Material Request Item-available_qty",
                    "Material Request Item-required_qty",

                    "Request for Quotation-budget_bom_reference",
                    "Request for Quotation-reference",
                    "Request for Quotation-section_break_10",
                    "Request for Quotation-fetch_mr",
                    "Request for Quotation-brand",
                    "Request for Quotation-item_group",
                    "Request for Quotation-supplier",
                    "Request for Quotation-warehouse",
                    "Request for Quotation Item-available_qty",
                    "Request for Quotation Item-required_qty",
                    "Manufacturing Settings-default_warehouse_for_request_for_quotation",
                    "Request for Quotation-references",
                    "Request for Quotation-material_request_reference",
                    "Request for Quotation Item-budget_bom_rate",
					"Purchase Receipt Item-po_qty",
					"Purchase Receipt Item-gate_pass_qty",
					"Stock Entry-budget_bom_reference",
					"Job Card-budget_bom_reference",
					"Stock Entry-reference",
					"Job Card-reference",
					"Pick List Item-work_order_item",
					"Work Order Item-picked_qty",
				]
			]
		]
	},
	{
		"doctype": "Property Setter",
		"filters": [
			[
				"name",
				"in",
				[
					"Purchase Order Item-schedule_date-in_list_view",
					"Work Order-additional_operating_cost-fetch_from",
					"Work Order-additional_operating_cost-fetch_if_empty",
					"Opportunity-main-links_order",
					"Quotation-status-default",
					"Quotation-status-options",
					"Opportunity-expected_closing-reqd",
					"Opportunity Item-qty-default",
					"Opportunity-status-options",
					"Job Card-quality_inspection-mandatory_depends_on",
					"Opportunity-status-default",
					"Opportunity-status-options"
				]
			]
		]
	}
]
