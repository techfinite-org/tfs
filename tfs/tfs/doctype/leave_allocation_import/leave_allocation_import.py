# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeaveAllocationImport(Document):
	def on_submit(self):
		self.get_all_label()

	def get_all_field_names(self):
		return [field.fieldname for field in self.meta.fields]

	def get_label_from_fieldname(self, fieldname):
		df = self.meta.get_field(fieldname)
		if df:
			return df.label

	def get_all_label(self):
		all_field_names = self.get_all_field_names()
		for all_label in all_field_names:
			label_name = self.get_label_from_fieldname(all_label)
			self.all_leave_type(label_name)

	def all_leave_type(self, label_name):
		all_leave_type_names = frappe.get_all('Leave Type', filters={}, fields=['name'])
		all_names = [doc.get('name') for doc in all_leave_type_names]
		for names in all_names:
			if names == label_name:
				field_name = self.get_field_name_by_label(label_name)
				value = getattr(self, field_name, 0)
				if value and value != 0:
					self.create_leave_allocation(names, field_name, self.from_date,self.to_date)

	def create_leave_allocation(self, names, field_name,from_date,to_date):
		# print("-------------------create_additional_salary-----------------", names, field_name)

		if field_name is not None:
			value = getattr(self, field_name, 0)
			if value is not None:
				leave_allocation = frappe.new_doc("Leave Allocation")
				leave_allocation.employee = self.employee
				leave_allocation.company = self.company
				leave_allocation.leave_type = names
				leave_allocation.from_date = from_date
				leave_allocation.to_date = to_date
				leave_allocation.new_leaves_allocated = value
				leave_allocation.leave_allocation_reference = self.name
				leave_allocation.save()
				leave_allocation.submit()

	def get_field_name_by_label(self, label_name):
		for field in self.meta.fields:
			if field.label == label_name:
				return field.fieldname
		return None

