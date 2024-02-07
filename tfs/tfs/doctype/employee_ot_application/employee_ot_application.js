// Copyright (c) 2024, Techfinite Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee OT Application', {
	on_submit: function(frm) {
		frappe.call({
			method:'tfs.tfs.doctype.employee_ot_application.employee_ot_application.insert_ot_balance',
			args:{
				"ot_hour":frm.doc.total_hours,
				"emp_id":frm.doc.employee 
			},callback:function(r){
				if(r.message = "no record"){
					frappe.throw(" No Record found ")
					
				}
			}
		})

	}
});
