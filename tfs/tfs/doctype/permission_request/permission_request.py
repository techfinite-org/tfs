import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class PermissionRequest(Document):
    def validate(self):
        # Check if both from_date_time and to_date_time are set
        if self.from_date_time and self.to_date_time:
            # Convert date-time strings to datetime objects
            
            from_datetime = datetime.strptime(str(self.from_date_time), "%Y-%m-%d %H:%M:%S")
            from_date = from_datetime.date()
            print("--------------------from_date--------------",from_date)
            to_datetime = datetime.strptime(str(self.to_date_time), "%Y-%m-%d %H:%M:%S")
            
            # Calculate the time difference in hours and round to two decimal places
            time_difference = round((to_datetime - from_datetime).total_seconds() / 3600, 2)
            
            # Set the calculated hours in the permission_hours field
            self.custom_from_date = from_date
            self.custom_permission_hours = time_difference
        else:
            # If either from_date_time or to_date_time is not set, set permission_hours to 0
            self.custom_from_date = 0
            self.custom_permission_hours = 0





    # def on_submit(self):
    #     # Create Employee Checkin document for IN
    #     employee_checkin = frappe.new_doc("Employee Checkin")
    #     print("--------------line no 8--------------------",employee_checkin)
    #     employee_checkin.set("time", self.from_date_time)
    #     employee_checkin.set("log_type", "IN")
    #     employee_checkin.set("employee", self.employee)
    #     employee_checkin.set("device_id", "Permission")
    #     employee_checkin.insert()

    #     # Create Employee Checkout document for OUT
    #     employee_checkout = frappe.new_doc("Employee Checkin")
    #     employee_checkout.set("time", self.to_date_time)
    #     employee_checkout.set("log_type", "OUT")
    #     employee_checkout.set("employee", self.employee)
    #     employee_checkout.set("device_id", "Permission")
    #     employee_checkout.insert()
