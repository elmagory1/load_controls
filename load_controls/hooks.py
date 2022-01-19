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
	"Quotation" : "public/js/quotation.js",
	"Material Request" : "public/js/material_request.js",
	"Opportunity" : "public/js/opportunity.js",
	"Sales Order" : "public/js/sales_order.js",
	"Supplier Quotation" : "public/js/supplier_quotation.js",
}
doctype_list_js = {
	"Quotation" : "public/js/quotation_list.js"
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
	"Quotation": {
		"on_submit": "load_controls.doc_events.quotation.submit_q",
		"on_cancel": "load_controls.doc_events.quotation.cancel_q",
	},
	"Material Request": {
		"on_submit": "load_controls.doc_events.utils.on_submit_record",
		"on_cancel": "load_controls.doc_events.utils.on_cancel_record",
		"on_trash": "load_controls.doc_events.utils.on_cancel_record",
		"validate": "load_controls.doc_events.material_request.validate_mr",
	},
	"Purchase Order": {
		"on_submit": "load_controls.doc_events.utils.on_submit_record",
		"on_cancel": "load_controls.doc_events.utils.on_cancel_record",
	},
	"Purchase Invoice": {
		"on_submit": "load_controls.doc_events.utils.on_submit_record",
		"on_cancel": "load_controls.doc_events.utils.on_cancel_record",
	},
	"Purchase Receipt": {
		"on_submit": "load_controls.doc_events.utils.on_submit_record",
		"on_cancel": "load_controls.doc_events.utils.on_cancel_record",
	},
	"Sales Order": {
		"on_submit": "load_controls.doc_events.sales_order.on_submit_so",
		"on_cancel": "load_controls.doc_events.sales_order.on_cancel_so",
	},
	"Delivery Note": {
		"on_submit": "load_controls.doc_events.utils.on_submit_record",
		"on_cancel": "load_controls.doc_events.utils.on_cancel_record",
	},
	"Sales Invoice": {
		"on_submit": "load_controls.doc_events.utils.on_submit_record",
		"on_cancel": "load_controls.doc_events.utils.on_cancel_record",
	},
	"Supplier Quotation": {
		"on_submit": "load_controls.doc_events.supplier_quotation.on_submit_sq",
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
                    "Delivery Note-references",
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
                    "Opportunity-project_name",
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
				]
			]
		]
	}
]
