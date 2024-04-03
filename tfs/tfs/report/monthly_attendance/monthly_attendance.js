// Copyright (c) 2024, Techfinite Systems and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Attendance"] = {
    "filters": [
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "reqd": 0
        },
        {
            "fieldname": "from_date",
            "label": __("FROM Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("TO Date"),
            "fieldtype": "Date",
            "reqd": 1
        }
    ],
    "formatter": function (value, row, column, data, default_formatter) {
        
            // Customize rendering for the "Present" columns
            if (value === "P") {
                return `<span style="color: green;">${__("P")}</span>`;
            } else if (value === "A") {
                return `<span style="color: red;">${__("A")}</span>`;
            } else if (value === "HD") {
                return `<span style="color: #FFA500;">${__("HD")}</span>`;
            }
			else if (value === "WO") {
                return `<span style="color: blue;">${__("WO")}</span>`;
            }
			else if (value === "H") {
                return `<span style="color: blue;">${__("H")}</span>`;
            }
			else if (value === "WOP") {
                return `<span style="color: #502195 ;">${__("WOP")}</span>`;
            }
			else if (value === "HOP") {
                return `<span style="color: #502195 ;">${__("HOP")}</span>`;
            }
			
        
        // Use default formatter for other columns
        return default_formatter(value, row, column, data);
    }
};
