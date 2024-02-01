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
    if not frappe.db.exists('Custom Field', 'Employee-custom_shift_group'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Employee',
            'fieldname': 'custom_shift_group',
            'label': 'Shift Group',
            'fieldtype': 'Link',
            'insert_after': 'Attendance Device ID (Biometric/RF tag ID)',
            'Options' : 'Shift Group',
            'reqd': 0  # Set to 1 if the field is required
        }).insert()

def add_custom_field_to_shift_type():
    if not frappe.db.exists('Custom Field', 'Shift Type-my_custom_field'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Shift Type',
            'fieldname': 'custom_shift_group',
            'label': 'Shift Group',
            'fieldtype': 'Link',
            'insert_after': 'Enable Auto Attendance',
            'Options' : 'Shift Group',
            'reqd': 0  # Set to 1 if the field is required
        }).insert()
