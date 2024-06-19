import frappe
from datetime import datetime, timedelta
import calendar
def check_email_queue_status():
    email_queue_records = frappe.get_all("Email Queue", filters={"status": "Not Sent"}, fields=["name"])
    
    for name in email_queue_records:
        record = frappe.get_doc("Email Queue", name)
        record.send()

@frappe.whitelist()
def add_cl_every_month():

    leave_allocations = frappe.get_all("Leave Allocation", filters={'leave_type': 'CL'}, fields=['name'])
    try:
        for allocation in leave_allocations:
            allocation_doc = frappe.get_doc("Leave Allocation", allocation.name)
            if hasattr(allocation_doc, 'new_leaves_allocated'):
                allocation_doc.new_leaves_allocated += 1
                allocation_doc.save()
                frappe.db.commit()
            else:
                frappe.log_error(f"'new_leaves_allocated' field does not exist in {allocation.name}", "add_permission")
    except Exception as e:
        frappe.log_error(f"Error updating Leave Allocation {allocation.name}: {str(e)}", "add_permission")


def get_month_date_range():
    # Get current date
    now = datetime.now()
    # Get the first day of the current month
    first_day = datetime(now.year, now.month, 1)
    # Get the last day of the current month
    last_day = calendar.monthrange(now.year, now.month)[1]
    last_day_date = datetime(now.year, now.month, last_day, 23, 59, 59)
    return first_day, last_day_date


@frappe.whitelist()
def permission_hours():
    from_date, to_date = get_month_date_range()
    print("From date (start of month):", from_date)
    print("To date (end of month):", to_date)
    print("---------------------------------Its working-------------------------")

    employees = frappe.get_all("Employee", fields=['name'])

    try:
        for emp in employees:
            leave_allocation = frappe.new_doc("Leave Allocation")
            leave_allocation.employee = emp.name
            leave_allocation.leave_type = "permission demo"
            leave_allocation.from_date = from_date
            leave_allocation.to_date = to_date
            leave_allocation.new_leaves_allocated = 90
            leave_allocation.submit()
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error creating Leave Allocation for employee {emp.name}: {str(e)}", "permission_hours")

@frappe.whitelist()
def schedule_cl_every_month():
    # Schedule the check_email_queue_status function to run periodically (e.g., every minutes)
    frappe.enqueue(add_cl_every_month, queue='long', timeout=600, job_name = "Add CL Every Month")


@frappe.whitelist()
def schedule_permission_every_month():
    # Schedule the check_email_queue_status function to run periodically (e.g., every minutes)
    frappe.enqueue(permission_hours, queue='long', timeout=600, job_name="Add Permission Hours Every Month")
@frappe.whitelist()    
def schedule_email_sender():    
    frappe.enqueue(check_email_queue_status, queue='long', timeout=600, job_name = "Email Queue")
    
