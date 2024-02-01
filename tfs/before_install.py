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
        custom_field = frappe.new_doc({
            'doctype': 'Custom Field',
            'dt': 'Employee',
            'fieldname': 'custom_shift_group',
            'label': 'Shift Group',
            'fieldtype': 'Link',
            'insert_after': 'Attendance Device ID (Biometric/RF tag ID)',
            'options': 'Shift Group',
            'reqd': 0  
        })
        custom_field.insert()
 
        # Ensure the doctype is hashable before adding to the template
        if 'Employee' not in frappe.local.new_doc_templates:
            frappe.local.new_doc_templates['Employee'] = []
 
        frappe.local.new_doc_templates['Employee'].append('custom_shift_group')
def add_custom_field_to_shift_type():
    if not frappe.db.exists('Custom Field', 'Shift Type-my_custom_field'):
        custom_field = frappe.new_doc({
            'doctype': 'Custom Field',
            'dt': 'Shift Type',
            'fieldname': 'my_custom_field',  
            'label': 'Shift Group',
            'fieldtype': 'Link',
            'insert_after': 'Enable Auto Attendance',
            'options': 'Shift Group',
            'reqd': 0  
        })
        custom_field.insert()
 
        # Ensure the doctype is hashable before adding to the template
        if 'Shift Type' not in frappe.local.new_doc_templates:
            frappe.local.new_doc_templates['Shift Type'] = []
 
        frappe.local.new_doc_templates['Shift Type'].append('my_custom_field')