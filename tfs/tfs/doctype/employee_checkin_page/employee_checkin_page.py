# Copyright (c) 2023, Techfinite Systems and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class EmployeeCheckinPage(Document):
	pass
# Copyright (c) 2023, techfinite and contributors
# For license information, please see license.txt

import frappe
import math
from frappe.model.document import Document
from frappe.utils.user import get_user_fullname
from frappe.utils import now_datetime
from frappe import _
class EmployeeCheckinPage(Document):
    pass
@frappe.whitelist()
def get_userdetails():
    user_details = {}
    user_id = frappe.session.user
    # frappe.msgprint(user_id)
    # Fetch company abbreviation
    designation_query = """
        SELECT employee, employee_name, branch, custom_range
        FROM tabEmployee
        WHERE user_id = %s AND `status` = 'Active'
    """

    employee_details_result = frappe.db.sql(designation_query, user_id, as_dict=True)
     
    if employee_details_result:
        for employee_detail in employee_details_result:
            user_details['employee'] = employee_detail.employee
            user_details['branch'] = employee_detail.branch
            user_details['custom_range'] = employee_detail.custom_range
          
    else:
        frappe.msgprint("No employee details found for the given user_id and status.")
    
    
    return user_details

@frappe.whitelist()
def employee_check_in(log_type, emp_longitude, emp_latitude):
    user_details = get_userdetails()

    # Define branch_query
    branch_query = """
        SELECT branch, custom_branch_longitude, custom_branch_latitude
        FROM tabBranch
        WHERE branch = %s 
    """
    print("--------------------------line no 48--------------------------",user_details['employee'],user_details['custom_range'])

    # Assuming user_details['branch'] is the branch value you want to query
    branch_result = frappe.db.sql(branch_query, user_details['branch'], as_dict=True)
    
    # Initialize branch_info
    branch_info = None
    branch_latitude = None
    branch_longitude = None

    if branch_result:
        for branch_info in branch_result:
    #         frappe.msgprint(f"Branch: {branch_info.branch}, Latitude: {branch_info.branch_latitude}, Longitude: {branch_info.branch_longitude}")
    # else:
    #     frappe.msgprint("No branch details found for the given branch.")

    # Check if branch_info is available before using it
            if branch_info:
                branch_latitude = branch_info.custom_branch_latitude
                branch_longitude = branch_info.custom_branch_longitude
                # frappe.msgprint(f"Branch: {branch_info.branch}, Latitude: {branch_latitude}, Longitude: {branch_longitude},")
                # rest of your code
            else:
                # Handle the case where branch_info is not available
                frappe.msgprint("Branch information not available.")
    
    # # Avoid using 'range' as a variable name
    # query = """
    # SELECT range
    # FROM tabAttendance Punch Settings   
    # """

    # # Execute the SQL query
    # range_result = frappe.db.sql(query, as_dict=True)

    # # Check if there are any results before accessing 'range' attribute
    # if range_result:
    #     print("-------------------------line no 79--------------------", range_result[0]['range'])
    # else:
    #     print("No results found.")

    # Radius of the Earth in kilometers
    R = 6371

    # Validate input
    # if not all(map(lambda x: isinstance(x, (int, float)), [emp_latitude, emp_longitude, branch_latitude, branch_longitude])):
    #     frappe.msgprint(_('Please enter valid coordinates.'))
    #     return None
    print("emp_latitude:", emp_latitude, type(emp_latitude))
    emp_latitude = float(emp_latitude)
    emp_longitude = float(emp_longitude)
    branch_latitude = float(branch_latitude)
    branch_longitude = float(branch_longitude)
    

    # Convert coordinates to radians
    φ1 = emp_latitude * math.pi / 180
    φ2 = branch_latitude * math.pi / 180
    Δφ = (branch_latitude - emp_latitude) * math.pi / 180
    Δλ = (branch_longitude - emp_longitude) * math.pi / 180

    # Haversine formula
    a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + \
        math.cos(φ1) * math.cos(φ2) * \
        math.sin(Δλ / 2) * math.sin(Δλ / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate distance in kilometers
    distance = R * c
    # frappe.msgprint(_('Distance: {0} kilometers'.format(round(distance, 2))))
    
    
    if distance is not None:
        if user_details:
            custom_range_str = user_details.get('custom_range', '')
            
            # Check if custom_range_str is not an empty string
            if custom_range_str:
                try:
                    custom_range = float(custom_range_str)
                except ValueError:
                    frappe.msgprint("Invalid Range value. Please provide a valid Range.")
                    return distance
            else:
                frappe.msgprint("Range value is empty. Please provide a valid Range.")
                return distance

            if distance > custom_range:
                frappe.msgprint(_('You are {0} kilometers away. You cannot punch.'.format(round(distance, 2))))
                
            else:
                
               if 'employee' in user_details:
                employee_checkin = frappe.new_doc("Employee Checkin")

                # Set both date and time using now_datetime()
                employee_checkin.set("time", now_datetime())
                employee_checkin.set("log_type", log_type)
                employee_checkin.set("employee", user_details['employee'])

                try:
                    employee_checkin.insert()

                    # Display success message based on log_type
                    if log_type == 'IN':
                        frappe.msgprint(_('You are in {0} kilometers. Successfully Punch IN.'.format(round(distance, 2))))
                    elif log_type == 'OUT':
                        frappe.msgprint(_('You are in {0} kilometers. Successfully Punch OUT.'.format(round(distance, 2))))
                    else:
                        frappe.msgprint("Unknown log type. Please provide a valid log type.")
                except frappe.exceptions.ValidationError:
                    frappe.msgprint("Check-in failed. Please try again.")
               else:
                frappe.msgprint("Employee details not available. Cannot perform check-in.")
        else:
            frappe.msgprint("Please contact the administrator.")

    return distance




