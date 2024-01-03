// Copyright (c) 2023, Techfinite Systems and contributors
// For license information, please see license.txt


frappe.ui.form.on('Control Panel', {
	
	debtors_process: function(frm){
		frappe.call({
			method:"",
			args:{},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw("Error While importing data")
				}
				else{
					frappe.msgprint("Debtors Reports are loaded")
				}
			}
		})
	},

	claimbook_process: function(frm){
		frappe.call({
			method:"",
			args:{},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw("Error While importing data")
				}
				else{
					frappe.msgprint("ClaimBook are loaded")
				}
			}
		})
	},
	
	settlement_advice_process: function(frm){
		frappe.call({
			method:"",
			args:{},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw("Error While importing data")
				}
				else{
					frappe.msgprint("Debtors Reports are loaded")
				}
			}
		})
	},

	bank_statement_process: function(frm){
		frappe.call({
			method:"",
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw("Error While importing data")
				}
				else{
					frappe.msgprint("Debtors Reports are loaded")
				}
			}
		})
	},

	payment_entry_process: function(frm){
		console.log("Hi")
		frappe.call({
			method:"agarwals.utils.payment_entry_job.create_payment_entries",
		})
	},

	insurance_mapping: function(frm) {
		frappe.call({
			method:"agarwals.utils.insurance_mapping.tag_insurance_pattern",
			args:{
				doctype:"Bank Transaction Stagging",
			},
			callback:function(r){
				if(r.message == "Success"){
					frappe.msgprint({
						title: __('Notification'),
						indicator: 'green',
						message: __('Payment Insurance Tagging process is done 😀')
					});
				}
			}
		})
	},
	bank_transaction_process: function(frm) {
		frappe.call({
			method:"agarwals.utils.bank_transaction_process.process",
			args:{
				tag: "Insurance",
			},
			callback:function(r){
				if(r.message == "Success"){
					frappe.msgprint({
						title: __('Notification'),
						indicator: 'green',
						message: __('Bank Transaction Processing is done 😀')
					});
				}
			}
		})
	}
});
