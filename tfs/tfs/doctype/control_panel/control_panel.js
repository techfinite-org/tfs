// Copyright (c) 2023, Techfinite Systems and contributors
// For license information, please see license.txt


// Transform done
frappe.ui.form.on('Control Panel', {

	debtors_transform: function(frm){
		frappe.call({
			method:"agarwals.utils.transform.transform",
			args:{
				type:"debtor_report"
			},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw("Error While Loading the File")
				}
				else{
					frappe.msgprint("debtors report are successfully transformed.")
				}
			}
		})
	},
	claimbook_transform: function(frm){
		frappe.call({
			method:"agarwals.utils.transform.transform",
			args:{
				type:"claimbook"
			},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw("Error While Loading the File")
				}
				else{
					frappe.msgprint("claimbooks are successfully transformed.")
				}
			}
		})
	},
	settlement_transform: function(frm){
		frappe.call({
			method:"agarwals.utils.transform.transform",
			args:{
				type:"settlement_advice"
			},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw("Error While Loading the File")
				}
				else{
					frappe.msgprint("settlement advices are successfully transformed.")
				}
			}
		})
	},
	bank_statement_transform: function(frm){
		frappe.call({
			method:"agarwals.utils.transform.transform",
			args:{
				type:"bank_statement"
			},
			callback:function(r){
				if(r.message != "Success"){
					frappe.throw("Error While Loading the File")
				}
				else{
					frappe.msgprint("bank statements are successfully transformed.")
				}
			}
		})
	},

	// Loading Processes done
	debtors_loading: function(frm){
		frappe.call({
			method:"agarwals.utils.importation_and_doc_creation.import_job",
			args:{
				doctype:"Debtors Report",
				type:"debtor_report"
			},
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

	// Done
	claimbook_loading: function(frm){
		frappe.call({
			method:"agarwals.utils.importation_and_doc_creation.import_job",
			args:{
				doctype:"ClaimBook",
				type:"claimbook"
			},
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
	
	settlement_loading: function(frm){
		frappe.call({
			method:"agarwals.utils.importation_and_doc_creation.import_job",
			args:{
				doctype:"Settlement Advice",
				type:"settlement_advice"
			},
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
	bank_statment_loading: function(frm){
		frappe.call({
			method:"agarwals.utils.importation_and_doc_creation.create_bank_statements",
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
	payment_entry_job: function(frm){
		console.log("Hi")
		frappe.call({
			method:"agarwals.utils.payment_entry_job.create_payment_entries",
			callback:function(r){
				// if(r.message != "Success"){
				// 	frappe.throw("Error While importing data")
				// }
				// else{
				// 	frappe.msgprint("Debtors Reports are loaded")
				// }
			}
		})

	},

});
