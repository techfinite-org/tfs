// Copyright (c) 2023, Techfinite Systems and contributors
// For license information, please see license.txt


frappe.ui.form.on('Control Panel', {
	process_debtors: function(frm){
		frappe.call({
			method:"agarwals.utils.run_transform.run_transform_process",
			args:{
				type:"debtors"
			},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw(r.message)
				}
				else{
					frappe.msgprint("Debtors Reports are loaded")
				}
			}
		})
	},

	process_claimbook: function(frm){
		frappe.call({
			method:"agarwals.utils.run_transform.run_transform_process",
			args:{
				type:"claimbook"
			},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw(r.message)
				}
				else{
					frappe.msgprint("ClaimBook are loaded")
				}
			}
		})
	},
	
	process_settlement_stagging: function(frm){
		frappe.call({
			method:"agarwals.utils.run_transform.run_transform_process",
			args:{
				type:"Settlement"
			},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw(r.message)
				}
				else{
					frappe.msgprint("Settlement Advice are loaded")
				}
			}
		})
	},

	process_transaction_stagging: function(frm){
		frappe.call({
			method:"agarwals.utils.run_transform.run_transform_process",
			args:{
				type:"transaction"
			},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw(r.message)
				}
				else{
					frappe.msgprint("Bank transaction are loaded")
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
