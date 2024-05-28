app_name = "tfs"
app_title = "Tfs"
app_publisher = "Techfinite Systems"
app_description = "TFS Utils"
app_email = "it-support@techfinite.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------
app_include_css = [ "/assets/tfs/css/tfs.css" ]
# include js, css files in header of desk.html
# app_include_js: {"data_exporter.js":"public/js/custom_data_exporter"} # type: ignore
# app_include_css = "/assets/tfs/css/tfs.css"
# app_include_js = "/assets/tfs/js/tfs.js"

# include js, css files in header of web template
# web_include_css = "/assets/tfs/css/tfs.css"
# web_include_js = "/assets/tfs/js/tfs.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tfs/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doctype_js = {
    "Leave Application": "public/js/leave_application_override.js",
    "Compensatory Leave Request": "public/js/compensatory_leave_request_override.js",
    "Employee Checkin": "public/js/employee_checkin-override.js",
    # "Data Import":"public/js/custom_data_import.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "tfs/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "tfs.utils.jinja_methods",
#	"filters": "tfs.utils.jinja_filters"
# }

# Installation
# ------------

after_install = "tfs.after_install.after_install"
# after_install = "tfs.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tfs.uninstall.before_uninstall"
# after_uninstall = "tfs.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "tfs.utils.before_app_install"
# after_app_install = "tfs.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "tfs.utils.before_app_uninstall"
# after_app_uninstall = "tfs.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tfs.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	
	"Compensatory Leave Request": "tfs.compensatory_leave_request_overrides.CustomCompensatoryLeaveRequest",
    "Shift Type": "tfs.shift_type_override.OverrideShiftType",
    "Leave Application":"tfs.leave_application_override.LeaveApplicationOverride",
    "Attendance":"tfs.attendance_override.AttendanceOverride",
    # "Employee Checkin" : "tfs.employee_checkin_overrides.OverrideEmployeeCheckin"
    # "ToDo": "custom_app.overrides.CustomToDo"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# } 
	"Employee Checkin": {
		"before_save": "tfs.emploee_checkin_override.assign_shift"
	}
	
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"tfs.tasks.all"
#	],
#	"daily": [
#		"tfs.tasks.daily"
#	],
#	"hourly": [
#		"tfs.tasks.hourly"
#	],
#	"weekly": [
#		"tfs.tasks.weekly"
#	],
#	"monthly": [
#		"tfs.tasks.monthly"
#	],
# }


# Testing
# -------

# before_tests = "tfs.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	# "frappe.desk.doctype.event.event.get_events": "tfs.event.get_events",
     
# }
# #
# each overriding function accepts a `data` argument;``
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "tfs.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tfs.utils.before_request"]
# after_request = ["tfs.utils.after_request"]

# Job Events
# ----------
# before_job = ["tfs.utils.before_job"]
# after_job = ["tfs.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"tfs.auth.validate"
# ]


#to check
scheduler_events = {
    "cron": {
		"*/30 * * * *" : [
			"tfs.tfs.doctype.agarwals_dashboard.agarwals_dashboard.value_updater"
		],
  	    "*/2 * * * *": [
			"tfs.tfs.email_queue.schedule_email_sender"
		]
	}
}

fixtures = [
	"Custom Field"
]
