import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from datetime import datetime, timedelta
from frappe import _
from frappe.utils import getdate, nowdate, cstr

class PermissionRequest(Document):
    def validate(self):
        validate_dates(self, self.from_date_time, self.to_date_time)

        if self.from_date_time and self.to_date_time:
            from_datetime = datetime.strptime(str(self.from_date_time), "%Y-%m-%d %H:%M:%S")
            to_datetime = datetime.strptime(str(self.to_date_time), "%Y-%m-%d %H:%M:%S")
            time_difference = round((to_datetime - from_datetime).total_seconds() / 3600, 2)

            self.custom_from_date = from_datetime.date()
            self.custom_permission_hours = time_difference
        else:
            self.custom_from_date = 0
            self.custom_permission_hours = 0
            
def validate_dates(doc, from_date, to_date):
    date_of_joining, relieving_date = frappe.db.get_value(
        "Employee", doc.employee, ["date_of_joining", "relieving_date"]
    )

    if getdate(from_date) > getdate(to_date):
        frappe.throw(_("To date cannot be less than from date"))

    if date_of_joining and getdate(from_date) < getdate(date_of_joining):
        frappe.throw(_("From date cannot be less than employee's joining date"))

    if relieving_date and getdate(to_date) > getdate(relieving_date):
        frappe.throw(_("To date cannot be greater than employee's relieving date"))

    # Check for overlap with existing PermissionRequest records
    existing_records = frappe.get_all(
        "Permission Request",
        filters={
            "employee": doc.employee,
            "docstatus": 1,  # Consider only submitted records
            "name": ["!=", doc.name],  # Exclude the current record
        },
        fields=["from_date_time", "to_date_time"],
    )

    for record in existing_records:
        if do_time_ranges_overlap(
            from_date, to_date, record.from_date_time, record.to_date_time
        ):
            frappe.throw(_("Time overlap with existing Permission Request"))

def do_time_ranges_overlap(start1, end1, start2, end2):
    # Convert date-time strings to datetime objects
    start1 = cstr(start1)
    end1 = cstr(end1)
    start2 = cstr(start2)
    end2 = cstr(end2)

    start1 = datetime.strptime(start1, "%Y-%m-%d %H:%M:%S")
    end1 = datetime.strptime(end1, "%Y-%m-%d %H:%M:%S")
    start2 = datetime.strptime(start2, "%Y-%m-%d %H:%M:%S")
    end2 = datetime.strptime(end2, "%Y-%m-%d %H:%M:%S")

    return start1 < end2 and start2 < end1

    # def on_submit(self):
    #     # Uncomment the following lines if you want to create Employee Checkin/Checkout documents
    #     # Create Employee Checkin document for IN
    #     employee_checkin = frappe.new_doc("Employee Checkin")
    #     employee_checkin.time = self.from_date_time
    #     employee_checkin.log_type = "IN"
    #     employee_checkin.employee = self.employee
    #     employee_checkin.device_id = "Permission"
    #     employee_checkin.insert()

    #     # Create Employee Checkout document for OUT
    #     employee_checkout = frappe.new_doc("Employee Checkin")
    #     employee_checkout.time = self.to_date_time
    #     employee_checkout.log_type = "OUT"
    #     employee_checkout.employee = self.employee
    #     employee_checkout.device_id = "Permission"
    #     employee_checkout.insert()
