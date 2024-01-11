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

	map_tpa_in_bill: function(frm) {
            frappe.call({
					method: "agarwals.utils.tpa_and_region_matcher.match_tpa",
					callback: function(r){
						var return_msg = r.message
						frappe.msgprint(return_msg)
					}
			})
        },
	map_region_in_bill:function(frm){
            frappe.call({
					method: "agarwals.utils.tpa_and_region_matcher.map_region",
					callback: function(r){
						var return_msg = r.message
						console.log(return_msg)
					}
			})
        },
	map_branch_type_in_bill:function(frm){
            frappe.call({
					method: "agarwals.utils.tpa_and_region_matcher.map_branch_type",
					callback: function(r){
						var return_msg = r.message
						console.log(return_msg)
					}
			})
        },

	create_sales_invoice:function(frm){
            frappe.call({
					method: "agarwals.utils.sales_invoice_creation_and_cancellation.create_sales_background_job",
					args: {
						n:1000
					},
					callback: function(r){
						var return_msg = r.message
						console.log(return_msg)
					}
			});
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
			method:"agarwals.utils.settlement_advice.advice_transform",
			args:{
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

	process_payment_entry: function(frm){
		console.log("Hi")
		frappe.call({
			method:"agarwals.utils.payment_entry_job.create_payment_entries",
		})
	},

	mapping_insurance: function(frm) {
		frappe.call({
			method:"agarwals.utils.insurance_mapping.tag_insurance_pattern",
			args:{
				doctype:"Bank Transaction Staging",
			},
			callback:function(r){
				if(r.message == "Done"){
					frappe.msgprint({
						title: __('Notification'),
						indicator: 'green',
						message: __('Payment Insurance Tagging process is done 😀')
					});
				}
			}
		})
	},
	process_bank_transaction: function(frm) {
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
	},
	process_settlement_advice: function(frm) {
		frappe.call({
			method:"agarwals.utils.settlement_advice_staging_process.process",
			args:{
			},
			callback:function(r){
				if(r.message == "Success"){
					frappe.msgprint({
						title: __('Notification'),
						indicator: 'green',
						message: __('Settlement Advice Staging transfer done')
					});
				}
				else{
					frappe.throw(r.message)
				}
			}
		})
	}
});


