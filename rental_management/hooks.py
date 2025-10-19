app_name = "rental_management"
app_title = "Blush & Glow Rental"
app_publisher = "clearmydesk"
app_description = "Rental Management for Blush & Glow"
app_email = "ananthcjayan@gmail.com"
app_license = "mit"
app_logo_url = "/assets/rental_management/images/blush_glow_logo.png"

# Apps
# ------------------

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "rental_management",
		"logo": "/assets/rental_management/images/blush_glow_logo.png",
		"title": "Blush & Glow Rental",
		"route": "/app/home",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/rental_management/css/rental_theme.css"
app_include_js = "/assets/rental_management/js/rental_desk.js"

# include js, css files in header of web template
# web_include_css = "/assets/rental_management/css/rental_management.css"
# web_include_js = "/assets/rental_management/js/rental_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "rental_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Payment Entry": "public/js/payment_entry.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "rental_management/public/icons.svg"

# Home Pages
# ----------
# Let Frappe handle the default home page (/app)
# Users will see the standard workspaces view

# Set Rental Management workspace as default
default_workspace = "Rental Management"



# Website brand and app logo
brand_html = """
<div class="app-logo navbar-brand-custom">
    <img src="/assets/rental_management/images/blush_glow_logo.png" 
         alt="Blush & Glow" 
         style="max-height: 40px; width: auto;" />
</div>
"""

# Website context
website_context = {
	"favicon": "/assets/rental_management/images/blush_glow_logo.png",
	"splash_image": "/assets/rental_management/images/blush_glow_logo.png",
}

# Desk customization
app_logo_url = "/assets/rental_management/images/blush_glow_logo.png"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "rental_management.utils.jinja_methods",
# 	"filters": "rental_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "rental_management.install.before_install"
# after_install = "rental_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "rental_management.uninstall.before_uninstall"
# after_uninstall = "rental_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "rental_management.utils.before_app_install"
# after_app_install = "rental_management.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "rental_management.utils.before_app_uninstall"
# after_app_uninstall = "rental_management.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rental_management.notifications.get_notification_config"

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
	"Item": {
		"before_save": "rental_management.automations.item_automation.before_item_save",
		"after_insert": "rental_management.automations.item_automation.after_item_insert",
        "on_update": "rental_management.automations.item_automation.on_item_update",
	},
	"Customer": {
		"before_save": "rental_management.automations.customer_automation.before_customer_save"
	},
	"Sales Invoice": {
		"validate": "rental_management.automations.booking_automation.validate_sales_invoice",
		"on_submit": "rental_management.automations.booking_automation.on_submit_sales_invoice"
	}
}

# Accounting Configuration
# ------------------------
# Add Third Party Owner as a party type for accounting entries
accounting_dimension_doctypes = ["Third Party Owner"]

# Third Party Owner as a party type
party_account_types = ["Third Party Owner"]

# Add Third Party Owner to party types for Journal Entry
get_party_account = "rental_management.utils.get_third_party_owner_account"

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"rental_management.tasks.all"
# 	],
# 	"daily": [
# 		"rental_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"rental_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"rental_management.tasks.weekly"
# 	],
# 	"monthly": [
# 		"rental_management.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "rental_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "rental_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "rental_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["rental_management.utils.before_request"]
# after_request = ["rental_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["rental_management.utils.before_job"]
# after_job = ["rental_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"rental_management.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Installation
# ------------

after_install = "rental_management.setup.install.after_install"

