import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, cint, date_diff, format_date, getdate

from hrms.hr.utils import (
	create_additional_leave_ledger_entry,
	get_holiday_dates_for_employee,
	get_leave_period,
	validate_active_employee,
	validate_dates,
	validate_overlap,
)


class CustomCompensatoryLeaveRequest(Document):
	# def validate_holidays(self):
	# 	print("\n\n\n\n\n\n\n\n ****************** This is validate ***************\n\n\n\n\n\n\n\n")
	# 	pass
	def validate(self):
		print("\n\n\n\n\n\n\n\n ****************** This is from validate overrides ***************\n\n\n\n\n\n\n\n")
		validate_active_employee(self.employee)
		validate_dates(self, self.work_from_date, self.work_end_date)
		if self.half_day:
			if not self.half_day_date:
				frappe.throw(_("Half Day Date is mandatory"))
			if (
				not getdate(self.work_from_date) <= getdate(self.half_day_date) <= getdate(self.work_end_date)
			):
				frappe.throw(_("Half Day Date should be in between Work From Date and Work End Date"))
		validate_overlap(self, self.work_from_date, self.work_end_date)
		# self.validate_holidays()
		self.validate_attendance()
		if not self.leave_type:
			frappe.throw(_("Leave Type is madatory"))

	def validate_attendance(self):
		attendance_records = frappe.get_all(
			"Attendance",
			filters={
				"attendance_date": ["between", (self.work_from_date, self.work_end_date)],
				"status": ("in", ["Present", "Work From Home", "Half Day"]),
				"docstatus": 1,
				"employee": self.employee,
			},
			fields=["attendance_date", "status"],
		)

		half_days = [entry.attendance_date for entry in attendance_records if entry.status == "Half Day"]

		if half_days and (not self.half_day or getdate(self.half_day_date) not in half_days):
			frappe.throw(
				_(
					"You were only present for Half Day on {}. Cannot apply for a full day compensatory leave"
				).format(", ".join([frappe.bold(format_date(half_day)) for half_day in half_days]))
			)

		if len(attendance_records) < date_diff(self.work_end_date, self.work_from_date) + 1:
			frappe.throw(_("You are not present all day(s) between compensatory leave request days"))

	def validate_holidays(self):
		holidays = get_holiday_dates_for_employee(self.employee, self.work_from_date, self.work_end_date)
		if len(holidays) < date_diff(self.work_end_date, self.work_from_date) + 1:
			if date_diff(self.work_end_date, self.work_from_date):
				msg = _("The days between {0} to {1} are not valid holidays.").format(
					frappe.bold(format_date(self.work_from_date)), frappe.bold(format_date(self.work_end_date))
				)
			else:
				msg = _("{0} is not a holiday.").format(frappe.bold(format_date(self.work_from_date)))

			frappe.throw(msg)