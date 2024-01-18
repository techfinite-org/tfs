from frappe.model.document import Document

class CustomCompensatoryLeaveRequest(Document):
	def validate(self):
		print("\n\n\n\n\n\n\n************* this is override function ************\n\n\n\n\n\n\n\n\n")
		
		# self.validate_holidays()
		# self.validate_attendance() 
		
   