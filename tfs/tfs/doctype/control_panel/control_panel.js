frappe.ui.form.on('Control Panel', {
	process_debtors: function (frm) {
		frappe.call({
			method: "agarwals.utils.run_transform.run_transform_process",
			args: {
				type: "debtors"
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {
					frappe.msgprint("Debtors Reports are loaded")
				}
			}
		})
	},
	process_claimbook: function (frm) {
		frappe.call({
			method: "agarwals.utils.run_transform.run_transform_process",
			args: {
				type: "claimbook"
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {
					frappe.msgprint("ClaimBook are loaded")
				}
			}
		})
	},
	process_settlement_staging: function (frm) {
		frappe.call({
			method: "agarwals.utils.settlement_advice.advice_transform",
			args: {
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {
					frappe.msgprint("Settlement Advice are loaded")
				}
			}
		})
	},
	process_transaction_staging: function (frm) {
		frappe.call({
			method: "agarwals.utils.run_transform.run_transform_process",
			args: {
				type: "transaction"
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {
					frappe.msgprint("Bank transaction are loaded")
				}
			}
		})
	},
	create_sales_invoice: function (frm) {
		frappe.call({
			method: "agarwals.utils.sales_invoice_creator.create_sales_invoice",
		});
	},
	mapping_insurance: function (frm) {
		frappe.call({
			method: "agarwals.utils.insurance_mapping.tag_insurance_pattern",
			args: {
				doctype: "Bank Transaction Staging",
			},
			callback: function (r) {
				if (r.message == "Done") {
					frappe.msgprint({
						title: __('Notification'),
						indicator: 'green',
						message: __('Insurance Tagging Process : Done')
					});
				}
			}
		})
	},
	process_bank_transaction: function (frm) {
		frappe.call({
			method: "agarwals.utils.bank_transaction_process.process",
			args: {
				tag: "Insurance",
			},
			callback: function (r) {
				if (r.message == "Success") {
					frappe.msgprint({
						title: __('Notification'),
						indicator: 'green',
						message: __('Bank Transaction Process : Done')
					});
				}
			}
		})
	},
	generate_claim_key: function (frm) {
		frappe.call({
			method: "agarwals.utils.claim_key_mapper.map_claim_key"
		})
	},
	process_payment_using_payment_entry: function (frm) {
		frappe.call({
			method: "agarwals.utils.run_transform.run_payment_entry",
		});
	},
	process_payment_using_journal_entry: function (frm) {
		frappe.call({
			method: "",
		})
	},
	process_settlement_advice: function (frm) {
		frappe.call({
			method: "agarwals.utils.settlement_advice_staging_process.process",
			args: {
			},
			callback: function (r) {
				if (r.message == "Success") {
					frappe.msgprint({
						title: __('Notification'),
						indicator: 'green',
						message: __('Settlement Advice Staging transfer done')
					});
				}
				else {
					frappe.throw(r.message)
				}
			}
		})
	},
	download_file: function (frm) {
		frappe.call({
			method: "agarwals.website_downloader.downloader_job.enqueue_job",
			args: {
				"tpa_name": frm.doc.tpa,
				"hospital_branch": frm.doc.branch
			}
		})
	},
	calculate_dso: function(frm) {
		frappe.call({
		   method:"agarwals.utils.dso_calculator.initiator",
		})
	}
});