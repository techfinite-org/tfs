# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt
# import frappe
from frappe.model.document import Document
import frappe
from frappe import _
from datetime import datetime, timedelta, time

class MarkAttendance(Document):
    pass

@frappe.whitelist()
def get_all_shift():
    shifts = frappe.get_all('Shift Type', filters={}, pluck='name')  # Add the fields you need
    return shifts  # Return the list if needed

@frappe.whitelist()
def update_shift_type_dates(process_attendance_after=None, last_sync_of_checkin=None):
    if not process_attendance_after or not last_sync_of_checkin:
        frappe.msgprint(_("Please provide valid values for Process Attendance After and Last Sync of Checkin"))
        return

    shifts = frappe.get_all("Shift Type", filters={}, fields=["name"])

    for shift in shifts:
        shift_type = shift.get('name')
        # Check if the Shift Type exists
        if not frappe.db.exists("Shift Type", shift_type):
            frappe.throw(_("Shift Type {0} does not exist").format(shift_type))
        # Fetch the Shift Type document
        shift_type_doc = frappe.get_doc("Shift Type", shift_type)
        # Update the fields
        shift_type_doc.process_attendance_after = process_attendance_after
        shift_type_doc.last_sync_of_checkin = last_sync_of_checkin
        # Save the changes
        shift_type_doc.save()
        frappe.db.commit()

        # Print success message (optional)
        print("Shift Type {0} updated successfully".format(shift_type))

@frappe.whitelist()
def run_daily_attendance():
    today = datetime.now().date()
    yesterday_date = today - timedelta(days=1)
    yesterday = datetime.combine(yesterday_date, time(22, 0, 0))
    update_shift_type_dates(yesterday_date, yesterday)
    shifts = frappe.get_all('Shift Type', filters={}, pluck='name')
    shifts_with_double_quotes = '[' + ','.join(f'"{shift}"' for shift in shifts) + ']'
    frappe.call('tfs.shift_type_override.enqueue_job',shift_list=shifts_with_double_quotes)
