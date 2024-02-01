from __future__ import unicode_literals
import frappe

def before_install():
    add_custom_fields()

def after_install():
    pass

def add_custom_fields():
    add_custom_field_to_employee()
    add_custom_field_to_shift_type()

def add_custom_field_to_employee():
    if not frappe.db.exists('Custom Field', 'Employee-my_custom_field'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Employee',
            'fieldname': 'my_custom_field',
            'label': 'My Custom Field',
            'fieldtype': 'Data',
            'insert_after': 'shift',
            'reqd': 1  # Set to 1 if the field is required
        }).insert()

def add_custom_field_to_shift_type():
    if not frappe.db.exists('Custom Field', 'Shift Type-my_custom_field'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Shift Type',
            'fieldname': 'my_custom_field',
            'label': 'My Custom Field',
            'fieldtype': 'Data',
            'insert_after': 'company',
            'reqd': 1  # Set to 1 if the field is required
        }).insert()
