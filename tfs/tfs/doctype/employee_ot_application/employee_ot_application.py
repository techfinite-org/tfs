import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class EmployeeOTApplication(Document):
    
    def validate(self):
        if self.from_time and self.to_time:
            from_time = datetime.strptime(str(self.from_time), "%H:%M:%S")
            to_time = datetime.strptime(str(self.to_time), "%H:%M:%S")
            time_difference = (to_time - from_time).total_seconds() / 3600
            self.total_hours = round(time_difference, 2)
        else:
            self.total_hours = 0
    # def on_submit(self):
    #     ot_balance_doc=frappe.get.doc({
    #         "doctype":"Employee OT Balance",
    #         "employee":self.employee
    #     })
    #     ot_balance_doc.ot_hours +=self.total_hours
    #     ot_balance_doc.save()
@frappe.whitelist()
def insert_ot_balance(ot_hour,emp_id):
    emp_id_value = frappe.db.get_value("Employee OT Balance",{"employee":emp_id},'employee')
    if emp_id_value == emp_id: 
        query = frappe.db.sql(f""" update `tabEmployee OT Balance` SET ot_hours = ot_hours+'{ot_hour}' WHERE employee = '{emp_id}'; """)
        frappe.db.commit()
    else:
        return "no record"
    
