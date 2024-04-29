from __future__ import unicode_literals
import frappe
from __future__ import unicode_literals
import frappe
import os
import shutil


def before_install():
    pass

def after_install():
    # add_custom_fields()
    overwite_twofactor()

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
            'fieldtype': 'Data',
            'insert_after': 'Attendance Device ID (Biometric/RF tag ID)',
            'reqd': 0  # Set to 1 if the field is required
        }).insert()

def add_custom_field_to_shift_type():
    if not frappe.db.exists('Custom Field', 'Shift Type-custom_shift_group'):
        frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Shift Type',
            'fieldname': 'custom_shift_group',
            'label': 'Shift Group',
            'fieldtype': 'Data',
            'insert_after': 'Enable Auto Attendance',
            'reqd': 0  # Set to 1 if the field is required
        }).insert()

def overwite_twofactor():
    original_transformer_path = frappe.get_app_path('frappe','twofactor.py')
    custom_transformer_path = frappe.get_app_path('tfs', 'override_twofactor.py')
    shutil.copyfile(custom_transformer_path, original_transformer_path)
    print("------------------------------------- TwoFactor Override Completed -------------------------------------")

def revert_twofactor():
    original_transformer_path = frappe.get_app_path('frappe','twofactor.py')
    custom_transformer_path = frappe.get_app_path('tfs', 'original_twofactor.py')
    shutil.copyfile(custom_transformer_path, original_transformer_path)
    print("------------------------------------- TwoFactor Revert Completed -------------------------------------")


