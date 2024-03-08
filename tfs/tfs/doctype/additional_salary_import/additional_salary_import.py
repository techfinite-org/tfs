# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
 
 
 
class AdditionalSalaryImport(Document):
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
            self.all_salary_component(label_name)
 
    def all_salary_component(self, label_name):
        all_salary_component_names = frappe.get_all('Salary Component', filters={}, fields=['name'])
        all_names = [doc.get('name') for doc in all_salary_component_names]
        for names in all_names:
            if names == label_name:
                field_name = self.get_field_name_by_label(label_name)
                value = getattr(self, field_name, 0)
                if value and value !=0 :
                    self.create_additional_salary(names, field_name)
 
    def create_additional_salary(self, names, field_name):
        # print("-------------------create_additional_salary-----------------", names, field_name)
 
        if field_name is not None:
            value = getattr(self, field_name, 0)
            if value is not None:
                try:
                    additional_salary = frappe.new_doc("Additional Salary")
                    additional_salary.employee = self.employee
                    additional_salary.salary_component = names
                    additional_salary.payroll_date = self.payroll_date
                    additional_salary.custom_additional_salary_reference = self.name
 
                    # Check if field_name is None before trying to get the attribute
                    additional_salary.amount = int(value)
                    # print("-------------------self.name-----------------", self.name)
 
                    additional_salary.save()
                    additional_salary.submit()
                except ValueError:
                    print(f"Could not convert value '{value}' to an integer.")
 
    def get_field_name_by_label(self, label_name):
        for field in self.meta.fields:
            if field.label == label_name:
                return field.fieldname
        return None
 
    def on_cancel(self):
        as_records = frappe.get_all('Additional Salary', filters={'custom_additional_salary_reference' : self.name}, pluck = 'name')
        for record in as_records:
            as_record = frappe.get_doc('Additional Salary',record)
            as_record.cancel()

        frappe.get_doc('Additional Salary Import', self.name).cancel()