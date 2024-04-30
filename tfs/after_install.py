from __future__ import unicode_literals
import frappe
import os
import shutil
import re

def before_install():
    pass

def after_install():
    # add_custom_fields()
    # overwrite_file(frappe.get_app_path('tfs','override_twofactor.py'),frappe.get_app_path('frappe','twofactor.py'))
    replace_content(frappe.get_app_path('tfs','override_twofactor.py'),frappe.get_app_path('frappe','twofactor.py'),r'^def send_token_via_sms',r'^def send_token_via_email',1,36)

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


def overwrite_file(file1_path, file2_path):
    try:
        with open(file1_path, 'r') as file1:
            content = file1.read()

        with open(file2_path, 'w') as file2:
            file2.write(content)
            
        print(f"Content from {file1_path} has been successfully overwritten to {file2_path}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Content from {file1_path} has been successfully overwritten to {file2_path} based on the given regex.")



def replace_content(file1_path, file2_path, start_pattern, end_pattern, insert_start, insert_end):
    try:
        start_index = None
        end_index = None
        with open(file1_path, 'r') as file1:
            insert_content = file1.readlines()[insert_start-1:insert_end] 

        with open(file2_path, 'r') as file2:
            content = file2.readlines()
            
        for index, line in enumerate(content):
            if re.match(start_pattern, line):
                start_index = index
            elif re.match(end_pattern, line) and start_index is not None:
                end_index = index
                break

        if start_index is not None and end_index is not None:
            content[start_index:end_index] = insert_content
        
        
        with open(file2_path, 'w') as file2:
            file2.writelines(content)

        print("Content has been successfully replaced.")

    except Exception as e:
        print(f"Error: {e}")


