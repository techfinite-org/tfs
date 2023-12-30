# For license information, please see license.txttruck_age

import frappe

# Define the get_filters function before execute
def get_filters(filters):
    base_filters = {}

    # Check if attendance_date is present in filters and has a valid date range
    if 'attendance_date' in filters and filters['attendance_date'][0] and filters['attendance_date'][1]:
        base_filters["attendance_date"] = ["between", [filters['attendance_date'][0], filters['attendance_date'][1]]]

    # Add other filters conditionally (employee and department)
    if 'employee' in filters and filters['employee']:
        base_filters["employee"] = filters['employee']

    if 'department' in filters and filters['department']:
        base_filters["department"] = filters['department']

    return base_filters

def execute(filters=None, dateRange=None):
    columns = [
        {"label": "Employee", "fieldname": "employee", "width": 130},
        {"label": "Employee Name", "fieldname": "employee_name", "width": 150},
        {"label": "Department", "fieldname": "department", "width": 120},
        {"label": "Present", "fieldname": "present", "width": 90},
        {"label": "Absent", "fieldname": "absent", "width": 90},
        {"label": "Half Day", "fieldname": "half_day", "width": 90},
        {"label": "On Leave", "fieldname": "on_leave", "width": 90},
        {"label": "Work From Home", "fieldname": "work_from_home", "width": 120},
        {"label": "Earned leave", "fieldname": "earned_leave", "width": 120},
        {"label": "Compensatory Off", "fieldname": "compensatory_off", "width": 150},
        {"label": "Sick Leave", "fieldname": "sick_leave", "width": 120}
    ]

    data = frappe.get_all('Attendance', filters=get_filters(filters), fields=['employee', 'employee_name', 'department', 'status', 'leave_type'])

    result = {}
    for row in data:
        employee = row['employee']
        if employee not in result:
            result[employee] = {
                "employee": row['employee'],
                "employee_name": row['employee_name'],
                "department": row['department'],
                "present": 0,
                "absent": 0,
                "half_day": 0,
                "on_leave": 0,
                "work_from_home": 0,
                "earned_leave": 0,
                "compensatory_off": 0,
                "sick_leave": 0
            }

        status = row['status']
        leave_type = row['leave_type']

        if status == 'Present':
            result[employee]['present'] += 1
        elif status == 'Absent':
            result[employee]['absent'] += 1
        elif status == 'Half Day':
            result[employee]['half_day'] += 1
        elif status == 'On Leave':
            result[employee]['on_leave'] += 1
        elif status == 'Work From Home':
            result[employee]['work_from_home'] += 1

        if leave_type == 'Earned leave':
            result[employee]['earned_leave'] += 1
        elif leave_type == 'Compensatory Off':
            result[employee]['compensatory_off'] += 1
        elif leave_type == 'Sick Leave':
            result[employee]['sick_leave'] += 1

    return columns, list(result.values())
