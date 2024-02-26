# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe



from frappe import _, get_user

def execute(filters=None):
    user = get_user()

    columns = [
        _("Employee ID") + ":Link/Employee:120",
        _("Employee Name") + "::150",
        _("Department") + "::120",
        _("Company") + "::120",
        _("Year") + ":Int:80",
        _("January") + "::80",
        _("February") + "::80",
        _("March") + "::80",
        _("April") + "::80",
        _("May") + "::80",
        _("June") + "::80",
        _("July") + "::80",
        _("August") + "::80",
        _("September") + "::80",
        _("October") + "::80",
        _("November") + "::80",
        _("December") + "::80",
        _("Total") + ":Int:80"
    ]

    data = []

    # Check if the user has Admin or HR Manager role
    if "Administrator" in frappe.get_roles(user.name) or "HR Manager" in frappe.get_roles(user.name):
        # Fetch data for all employees
        employees = frappe.get_all("Employee", fields=["name"])
    else:
        # Fetch data for the current user (employee)
        employees = frappe.get_all("Employee", filters={"user_id": user.name}, fields=["name"])

    for emp in employees:
        employee_id = emp.name

        # Fetch data for the employee
        for employee in frappe.db.sql("""
            SELECT te.employee AS Employee_ID,
                te.employee_name AS Employee_Name,
                te.department AS Department,
                te.company AS Company,
                YEAR(tla.from_date) AS Year,
                SUM(IF(MONTHNAME(tla.from_date) = 'January', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS January,
                SUM(IF(MONTHNAME(tla.from_date) = 'February', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS February,
                SUM(IF(MONTHNAME(tla.from_date) = 'March', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS March,
                SUM(IF(MONTHNAME(tla.from_date) = 'April', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS April,
                SUM(IF(MONTHNAME(tla.from_date) = 'May', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS May,
                SUM(IF(MONTHNAME(tla.from_date) = 'June', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS June,
                SUM(IF(MONTHNAME(tla.from_date) = 'July', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS July,
                SUM(IF(MONTHNAME(tla.from_date) = 'August', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS August,
                SUM(IF(MONTHNAME(tla.from_date) = 'September', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS September,
                SUM(IF(MONTHNAME(tla.from_date) = 'October', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS October,
                SUM(IF(MONTHNAME(tla.from_date) = 'November', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS November,
                SUM(IF(MONTHNAME(tla.from_date) = 'December', IF(tla.leave_type = 'Leave Without Pay', 1, 0), 0)) AS December,
                SUM(IF(tla.leave_type = 'Leave Without Pay', 1, 0)) AS Total
            FROM `tabLeave Application` tla
            JOIN `tabEmployee` te ON tla.employee = te.employee
            WHERE te.employee = %s AND YEAR(tla.from_date) >= YEAR(te.date_of_joining)
                AND YEAR(tla.from_date) <= YEAR(CURDATE())
            GROUP BY te.employee, YEAR(tla.from_date)
            ORDER BY YEAR(tla.from_date), te.employee""", (employee_id,), as_dict=True):

            data.append([
                employee.Employee_ID,
                employee.Employee_Name,
                employee.Department,
                employee.Company,
                employee.Year,
                employee.January,
                employee.February,
                employee.March,
                employee.April,
                employee.May,
                employee.June,
                employee.July,
                employee.August,
                employee.September,
                employee.October,
                employee.November,
                employee.December,
                employee.Total
            ])

    return columns, data
