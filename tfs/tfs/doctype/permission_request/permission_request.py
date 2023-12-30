import frappe
from frappe.model.document import Document

class PermissionRequest(Document):
    def on_submit(self):
        # Create Employee Checkin document for IN
        employee_checkin = frappe.new_doc("Employee Checkin")
        print("--------------line no 8--------------------",employee_checkin)
        employee_checkin.set("time", self.from_date_time)
        employee_checkin.set("log_type", "IN")
        employee_checkin.set("employee", self.employee)
        employee_checkin.set("device_id", "Permission")
        employee_checkin.insert()

        # Create Employee Checkout document for OUT
        employee_checkout = frappe.new_doc("Employee Checkin")
        employee_checkout.set("time", self.to_date_time)
        employee_checkout.set("log_type", "OUT")
        employee_checkout.set("employee", self.employee)
        employee_checkout.set("device_id", "Permission")
        employee_checkout.insert()
