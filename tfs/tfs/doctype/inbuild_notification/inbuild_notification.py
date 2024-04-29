# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class InbuildNotification(Document):
	def check_dublicate(self):
			dublicate_record_query = frappe.db.sql(f"SELECT * FROM `tabInbuild Notification` WHERE  type = '{self.type}' AND method = '{self.method}'")
			if dublicate_record_query:
					frappe.throw("Notification Alredy Exits")


	def before_insert(self):
			self.check_dublicate()
