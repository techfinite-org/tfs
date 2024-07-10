# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

# import frappe

import re
from frappe.exceptions import DoesNotExistError, ValidationError
import frappe
from datetime import datetime, timedelta
status_map = {
	"Present": "PI",
	"Absent": "A",
	"Half Day": "HD",
	"Work From Home": "WFH",
	"On Leave": "L",
	"Holiday": "H",
	"Weekly Off": "WO",
	"Weekly Off Present":"WOP",
	"Holiday Present" : "HOP"
}
def get_message() -> str:
	message = ""
	colors = ["green", "red", "orange", "green", "#318AD8", "", "","",""]

	count = 0
	for status, abbr in status_map.items():
		message += f"""
			<span style='border-left: 2px solid {colors[count]}; padding-right: 12px; padding-left: 5px; margin-right: 3px;'>
				{status} - {abbr}
			</span>
		"""
		count += 1

	return message
day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def generate_date_range(from_date_str, to_date_str):
    # Convert string dates to datetime objects
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

    # Generate the date range
    date_range = [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1)]

    # Convert datetime objects back to string format
    date_range_str = [date.strftime("%Y-%m-%d") for date in date_range]

    return date_range_str

# ... (your existing code)

def execute(filters=None):
    columns = []
    data = []
    attendance_filter = ""
    message = get_message()
    if 'from_date' in filters and 'to_date' in filters:
        to_date = filters['to_date']
        from_date = filters['from_date']
        attendance_filter += f"attendance_date >= '{from_date}' AND attendance_date <= '{to_date}' "

    if 'employee' in filters:
        employee = filters['employee']
        attendance_filter += f" AND employee = '{employee}'"

    date_column = generate_date_range(from_date, to_date)

    # Adding columns to the report
    columns.extend([
        {"label": "Employee ID", "fieldtype": "Link", "options": "Employee", "fieldname": "employee", "width": 120},
        {"label": "Employee Name", "fieldtype": "Data", "fieldname": "employee_name", "width": 120},
        {"label": "Designation", "fieldtype": "Data", "fieldname": "designation", "width": 120},
        {"label": "Department", "fieldtype": "Data", "fieldname": "department", "width": 120}
    ])

    # Adding date columns to the report
    for i in date_column:
        day_part = datetime.strptime(i, "%Y-%m-%d").day
        col = {"label": str(day_part), "fieldtype": "Data", "fieldname": i, "width": 50}
        columns.append(col)

    # Add columns for status sums
    status_columns = [
        {"label": "P", "fieldtype": "Data", "fieldname": "sum_present", "width": 50},
        {"label": "A", "fieldtype": "Data", "fieldname": "sum_absent", "width": 50},
        {"label": "HD", "fieldtype": "Data", "fieldname": "sum_half_day", "width": 50},
        {"label": "L", "fieldtype": "Data", "fieldname": "sum_leave", "width": 50},
        {"label": "WFH", "fieldtype": "Data", "fieldname": "sum_work_from_home", "width": 80},
        {"label": "WO", "fieldtype": "Data", "fieldname": "sum_weekly_off", "width": 80},
        {"label": "H", "fieldtype": "Data", "fieldname": "sum_holiday", "width": 50},
        {"label": "WOP", "fieldtype": "Data", "fieldname": "sum_weekly_off_present", "width": 80},
        {"label": "HOP", "fieldtype": "Data", "fieldname": "sum_holiday_present", "width": 80},
        {"label": "Total Present", "fieldtype": "Data", "fieldname": "sum_p_wop_hop", "width": 90},
        {"label": "Late Entry", "fieldtype": "Data", "fieldname": "late_entry", "width": 90},  
        {"label": "Total Working Hours", "fieldtype": "Data", "fieldname": "working_hours_count", "width": 90}, 
    ]
    columns.extend(status_columns)	
    # Adding columns for leave types
# Fetching leave types
    leave_types = frappe.get_all("Leave Type", filters={"custom_hourly":0}, fields=["name"])

# Iterating over leave types and adding columns
    for lt in leave_types:
       leave_type_col = {
			"label": lt["name"],
			"fieldtype": "Data",
			"fieldname": lt["name"].replace(" ", "_").lower(),
			"width": 50
		}
       columns.append(leave_type_col)

    # Getting a list of employees dynamically
    employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name"])
    
    if 'employee' in filters:
       employees = [e for e in employees if e.name == filters['employee']]
    # Inserting dummy data for testing
    for employee in employees:
        employee_id = employee.get("name")

        # Use frappe.get_doc to get the Employee document
        employee_doc = frappe.get_doc("Employee", employee_id)

        # Accessing attributes from the Employee document
        employee_details = {
            "employee_name": employee_doc.employee_name,
            "designation": employee_doc.designation,
            "department": employee_doc.department,
            "holiday_list": employee_doc.holiday_list
        }

        # Creating a row with employee details and attendance data
        row_data = [
            employee_id,
            employee_details["employee_name"],
            employee_details["designation"],
            employee_details["department"]
        ]

        attendance_records = frappe.get_all(
            "Attendance",
            filters={"employee": employee_id, "docstatus":1,"attendance_date": ["between", (from_date, to_date)]},
            fields=["attendance_date", "status","leave_type","attendance_request","working_hours"]
        )
        print("--------------------------employee_id---------------------",employee_id)
        leave_type_map = get_leave_type(attendance_records,date_column)
        leave_type_counts = get_leave_type_count(attendance_records, leave_types)
        attendance_request_map = get_attendance_request(attendance_records,date_column)
        working_hours_count = get_total_working_hours(attendance_records)
        print("--------------------working_hours_count-----------------------",working_hours_count)
        # print("--------------------------attendance_request_map-----------------------",attendance_request_map)
        # Create a map of attendance dates to statuses
        attendance_status_map = {record["attendance_date"].strftime("%Y-%m-%d"): record["status"] for record in attendance_records}
        # print("-------------------attendance_status_map---------------",attendance_status_map)
        
        # print("---------------------leave_type_map-----------------",leave_type_map)
        holiday_status_map = get_holiday_status(employee_doc, date_column)
        unmarked_attendance_map = get_unmarked_attendance(attendance_status_map, date_column, holiday_status_map)
        # print("------------------print(unmarked)--------------------",unmarked_attendance_map)
        holiday_present_map = get_holiday_present(employee_doc, date_column, attendance_status_map)
        late_entry_map = get_late_entry_sum(employee_doc, date_column)
        late_entry_value = late_entry_map
        # print("-------------------------------late_entry_map-----------------------",late_entry_map)
        
        status_counts = {
            "P": 0, "A": 0, "HD": 0, "L": 0,
            "WFH": 0, "WO": 0, "H": 0, "WOP": 0, "HOP": 0
        }
        for date in date_column:
            status = attendance_status_map.get(date, '')
            print("status:",status)
            leave_type_status = leave_type_map.get(date, '')
            holiday_status = holiday_status_map.get(date, '')
            holiday_present = holiday_present_map.get(date, '') 
            unmarked_attendance = unmarked_attendance_map.get(date, '')
            
            attendance_request_reason = attendance_request_map.get(date, '')
            # print("------------------attendance_request_reason--------------",attendance_request_reason)
            # print("------------------status---------------",status)
            # print("-----------------holiday_present-----------------",holiday_present)
            if status == 'Present':
                if holiday_present == 'Weekly Off Present':
                    status_abbreviation = 'WOP'
                    status_counts["WOP"] += 1
                elif holiday_present == 'Holiday Present':
                    status_abbreviation = 'HOP'
                    status_counts["HOP"] += 1
                elif attendance_request_reason == 'Work From Home':    
                    status_abbreviation = 'P(WFH)'
                    status_counts["P"] += 1
                elif attendance_request_reason == 'On Duty' :
                    status_abbreviation = 'P(OD)'  
                    status_counts["P"] += 1
                else:
                    status_abbreviation = 'P'
                    status_counts["P"] += 1
            elif status == 'Absent':
                status_abbreviation = 'A'
                status_counts["A"] += 1
            elif status == 'Half Day':
                leave_type_lwp = frappe.get_value('Leave Type', {'name': leave_type_status,}, ['is_lwp'])
                if holiday_present == 'Weekly Off Half Day': 
                    status_abbreviation = 'WOP\u00BD'
                    status_counts["WOP"] += 0.5	
                elif holiday_present == 'Holiday Half Day': 
                    status_abbreviation = 'HOP\u00BD'
                    status_counts["HOP"] += 0.5	
                elif leave_type_status: 
                    if leave_type_lwp == 1: 	
                       status_abbreviation = f'L({leave_type_status})\u00BD'
                    else:
                       status_abbreviation = f'L({leave_type_status})\u00BDHD'     
                       status_counts["HD"] += 1
                    status_counts["L"] += 0.5    
                elif attendance_request_reason == 'Work From Home':  
                    status_abbreviation = 'HD(WFH\u00BD)'   
                    status_counts["HD"] += 1
                elif attendance_request_reason == 'On Duty':     
                    status_abbreviation = 'HD(OD\u00BD)'
                    status_counts["HD"] += 1   
                else:    
                    status_abbreviation = 'HD'
                    status_counts["HD"] += 1
            elif status == 'On Leave':
                if leave_type_status:
                    status_abbreviation = f'L({leave_type_status})'
                else:
                    status_abbreviation = 'L'
                status_counts["L"] += 1
            elif status == 'Work From Home':
                status_abbreviation = 'WFH'
                status_counts["WFH"] += 1
            elif holiday_status == 'Weekly Off':
                status_abbreviation = 'WO'
                status_counts["WO"] += 1
            elif holiday_status == 'Holiday':
                status_abbreviation = 'H'
                status_counts["H"] += 1
            elif holiday_present == 'Weekly Off Present':  
                status_abbreviation = 'WOP'
                status_counts["WOP"] += 1
            elif holiday_present == 'Holiday Present':  
                status_abbreviation = 'HOP'    
                status_counts["HOP"] += 1
            elif unmarked_attendance == 'Unmarked':  
                status_abbreviation = 'A'    
                status_counts["A"] += 1    
            else:
                # You can handle other statuses or leave them empty as needed
                status_abbreviation = ''

            row_data.append(status_abbreviation)


        # Append status sums to the row_data
        for key in status_counts:
            row_data.append(status_counts[key])
        sum_p_wop_hop = status_counts["P"] + status_counts["WOP"] + status_counts["HOP"] +  0.5 * status_counts["HD"]
        # print("-------------------------------sum_p_wop_hop-----------------------------",sum_p_wop_hop)
        row_data.append(sum_p_wop_hop)  # Add the sum to the row_data
        row_data.append(late_entry_value)
        row_data.append(working_hours_count)
        row_data.extend(leave_type_counts)
        
     
        # Append the row_data to the data list
        data.append(row_data)
        

    # Prepare the HTML message
    html_message = f"""
        <div>
            <p style="font-weight: bold;">Status Abbreviations:</p>
            {message}
        </div>
    """


    return columns, data, html_message




def get_holiday_status(employee_doc, date_column):
    # Check if holiday_list is empty
    if not employee_doc.holiday_list:
        return {}

    try:
        holiday_list = frappe.get_doc('Holiday List', employee_doc.holiday_list)
    except DoesNotExistError:
        # Handle the case where the Holiday List does not exist
        frappe.throw(f"Holiday List '{employee_doc.holiday_list}' not found for employee '{employee_doc.name}'",
                     ValidationError)

    holiday_status_map = {}

    for date in date_column:
        # Query for the holiday on the specified day
        holiday_date_str = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        holiday = frappe.get_value('Holiday', {
            'parent': holiday_list.name,
            'holiday_date': holiday_date_str,
        }, ['weekly_off'])

        if holiday is not None:
            holiday_status_map[date] = "Weekly Off" if holiday == 1 else "Holiday"
        else:
            holiday_status_map[date] = None

    return holiday_status_map

def get_holiday_present(employee_doc, date_column, attendance_status_map):
    # Check if holiday_list is empty
    if not employee_doc.holiday_list:
        return {}

    try:
        holiday_list = frappe.get_doc('Holiday List', employee_doc.holiday_list)
    except DoesNotExistError:
        # Handle the case where the Holiday List does not exist
        frappe.throw(f"Holiday List '{employee_doc.holiday_list}' not found for employee '{employee_doc.name}'",
                     ValidationError)

    holiday_present_map = {}

    for date in date_column:
        # Query for the holiday on the specified day
        holiday_date_str = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        holiday = frappe.get_value('Holiday', {
            'parent': holiday_list.name,
            'holiday_date': holiday_date_str,
        }, ['weekly_off'])

        if holiday is not None:
            # Check if it's a weekly off
            if holiday == 1:
                # Check if attendance is marked as present or half-day
                if attendance_status_map.get(date) == 'Present':
                    holiday_present_map[date] = 'Weekly Off Present'
                elif attendance_status_map.get(date) == 'Half Day':
                    holiday_present_map[date] = 'Weekly Off Half Day'
                else:
                    holiday_present_map[date] = 'Weekly Off'
            else:
                # Check if attendance is marked as present or half-day
                if attendance_status_map.get(date) == 'Present':
                    holiday_present_map[date] = 'Holiday Present'
                elif attendance_status_map.get(date) == 'Half Day':
                    holiday_present_map[date] = 'Holiday Half Day'
                else:
                    holiday_present_map[date] = 'Holiday'
        else:
            holiday_present_map[date] = None

    return holiday_present_map





def get_late_entry_sum(employee_doc, date_column):
    late_entry_sum = 0
    # print("--------------------employee_doc.name-------------------",employee_doc.name)
    for date in date_column:
        late_entry_records = frappe.get_all(
            "Employee Checkin",
            filters={"employee": employee_doc.name, "docstatus": 0, "time": ["between", (f"{date} 00:00:00", f"{date} 23:59:59")]},
            fields=["time", "custom_late_entry"]
        )

        if late_entry_records:
            late_entry_value = late_entry_records[0].get("custom_late_entry")

            # Check if late_entry_value is a string
            if isinstance(late_entry_value, str):
                # Extract hours and minutes using regular expression
                match = re.match(r'(\d+):(\d+) Hr', late_entry_value)
                
                if match:
                    hours, minutes = map(int, match.groups())
                    late_entry_sum += hours * 60 + minutes
                    # print(f"------------------------------late_entry for {date}------------------------", late_entry_value)
                elif "Min" in late_entry_value:
                    minutes = int(late_entry_value.split(" ")[0])
                    late_entry_sum += minutes

    return late_entry_sum

def get_unmarked_attendance(attendance_status_map, date_column, holiday_status_map):
    unmarked_dates = {}
    for day in date_column:
        if day not in attendance_status_map:
            status = holiday_status_map.get(day, None)  # Get the status from holiday_status_map for the current day
            if status is None:
                unmarked_dates[day] = "Unmarked"
            # elif status != 'Holiday':
            #     unmarked_dates[day] = "Not a holiday"
    return unmarked_dates

def get_leave_type(attendance_records, date_column):
    leave_type = {}
    
    # Assuming attendance_records is a list of dictionaries with keys 'attendance_date', 'status', and 'leave_type'
    attendance_leave_type_map = {
        record["attendance_date"].strftime("%Y-%m-%d"): record["leave_type"]
        for record in attendance_records
        if record["status"] in ["On Leave", "Half Day"]
    }
    
    if attendance_leave_type_map:
        for day in date_column:
            leave_status = attendance_leave_type_map.get(day, None)
            if leave_status is not None:
                leave_type[day] = leave_status
    
    return leave_type


def get_leave_type_count(attendance_records, leave_types):
    leave_type_count = {lt["name"]: 0 for lt in leave_types}
    
    for record in attendance_records:
        if record.leave_type in leave_type_count:
            if record.status == "Half Day":
                leave_type_count[record.leave_type] += 0.5
            else:
                leave_type_count[record.leave_type] += 1
    
    return [leave_type_count.get(lt["name"], 0) for lt in leave_types]


def get_attendance_request(attendance_records, date_column):
    attendance_request_status = {}
    for record in attendance_records:
        attendance_records_name = record.get("attendance_request")
        attendance_date = record.get("attendance_date")
        attendance_date_str = attendance_date.strftime("%Y-%m-%d")
        ar_status = None
        for date in date_column:
            if date == attendance_date_str:
                ar_status = frappe.get_value("Attendance Request", {"name": attendance_records_name}, "reason")
                attendance_request_status[date] = ar_status
    return attendance_request_status    

def get_total_working_hours(attendance_records):
    total_hours_sum = 0
    for record in attendance_records:
        attendance_working_hours = record.get("working_hours")
        total_hours_sum += attendance_working_hours
    return round(total_hours_sum)   



            