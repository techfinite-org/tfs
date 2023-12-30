frappe.query_reports["Attendance Report"] = {
    "filters": [
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "reqd": 0
        },
        {
            "fieldname": "attendance_date",
            "label": __("Date"),
            "fieldtype": "DateRange",
            "reqd": 0,
            "operator": "between"
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "reqd": 0
        }
    ]

};



