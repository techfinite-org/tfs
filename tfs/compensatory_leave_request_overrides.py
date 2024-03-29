import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, cint, date_diff, format_date, getdate, time_diff_in_seconds

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
		leave_type_doc = frappe.get_doc('Leave Type', self.leave_type) 
		if leave_type_doc and leave_type_doc.custom_hourly == 1:
			return
		elif len(attendance_records) < date_diff(self.work_end_date, self.work_from_date) + 1:
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
   
	def on_submit(self):
		company = frappe.db.get_value("Employee", self.employee, "company")
		leave_type_doc = frappe.get_doc('Leave Type', self.leave_type) 
		if leave_type_doc and leave_type_doc.custom_hourly == 1:
			date_time_difference = time_diff_in_seconds(self.custom_work_end_date_time, self.custom_work_from_date_time) / 60
			date_difference = date_time_difference
		else :
			date_difference = date_diff(self.work_end_date, self.work_from_date) + 1

		if self.half_day:
			date_difference -= 0.5
		leave_period = get_leave_period(self.work_from_date, self.work_end_date, company)
		# print(leave_period)
		if leave_period:
			leave_allocation = self.get_existing_allocation_for_period(leave_period)
			# print("--------------------------------leave_allocation------------------------",leave_allocation)
			if leave_allocation:
				leave_allocation.new_leaves_allocated += date_difference
				leave_allocation.validate()
				leave_allocation.db_set("new_leaves_allocated", leave_allocation.total_leaves_allocated)
				leave_allocation.db_set("total_leaves_allocated", leave_allocation.total_leaves_allocated)

				# generate additional ledger entry for the new compensatory leaves off
				create_additional_leave_ledger_entry(
					leave_allocation, date_difference, add_days(self.work_end_date, 1)
				)
			else:
				leave_allocation = self.create_leave_allocation(leave_period, date_difference)
			self.db_set("leave_allocation", leave_allocation.name)
		else:
			frappe.throw(
				_("There is no leave period in between {0} and {1}").format(
					format_date(self.work_from_date), format_date(self.work_end_date)
				)
			)

	def on_cancel(self):
		if self.leave_allocation:
			date_difference = date_diff(self.work_end_date, self.work_from_date) + 1
			if self.half_day:
				date_difference -= 0.5
			leave_allocation = frappe.get_doc("Leave Allocation", self.leave_allocation)
			if leave_allocation:
				leave_allocation.new_leaves_allocated -= date_difference
				if leave_allocation.new_leaves_allocated - date_difference <= 0:
					leave_allocation.new_leaves_allocated = 0
				leave_allocation.validate()
				leave_allocation.db_set("new_leaves_allocated", leave_allocation.total_leaves_allocated)
				leave_allocation.db_set("total_leaves_allocated", leave_allocation.total_leaves_allocated)

				# create reverse entry on cancelation
				create_additional_leave_ledger_entry(
					leave_allocation, date_difference * -1, add_days(self.work_end_date, 1)
				)

	def get_existing_allocation_for_period(self, leave_period):
		leave_allocation = frappe.db.sql(
			"""
			select name
			from `tabLeave Allocation`
			where employee=%(employee)s and leave_type=%(leave_type)s
				and docstatus=1
				and (from_date between %(from_date)s and %(to_date)s
					or to_date between %(from_date)s and %(to_date)s
					or (from_date < %(from_date)s and to_date > %(to_date)s))
		""",
			{
				"from_date": leave_period[0].from_date,
				"to_date": leave_period[0].to_date,
				"employee": self.employee,
				"leave_type": self.leave_type,
			},
			as_dict=1,
		)

		if leave_allocation:
			return frappe.get_doc("Leave Allocation", leave_allocation[0].name)
		else:
			return False

	def create_leave_allocation(self, leave_period, date_difference):
		is_carry_forward = frappe.db.get_value("Leave Type", self.leave_type, "is_carry_forward")
		allocation = frappe.get_doc(
			dict(
				doctype="Leave Allocation",
				employee=self.employee,
				employee_name=self.employee_name,
				leave_type=self.leave_type,
				from_date=add_days(self.work_end_date, 1),
				to_date=leave_period[0].to_date,
				carry_forward=cint(is_carry_forward),
				new_leaves_allocated=date_difference,
				total_leaves_allocated=date_difference,
				description=self.reason,
			)
		)
		allocation.insert(ignore_permissions=True)
		allocation.submit()
		return allocation

@frappe.whitelist()
def hide_unhide_date_time_field(leave_type):
	leave_type_doc = None

	if leave_type:
		leave_type_doc = frappe.get_doc('Leave Type', leave_type)

	# Check if leave_type_doc is not None and has 'custom_hourly' attribute
	if leave_type_doc and leave_type_doc.custom_hourly == 1:
		# print("----------------------",leave_type_doc.custom_hourly)
		return leave_type_doc.custom_hourly

	# Return 'hide' if leave_type is provided but another variable is not found
	if leave_type:
		return 'hide'