frappe.ui.form.on('Control Panel', {
	process_debtors: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.transform.process",
			args: {
				args: {"type":"debtors","step_id":""}
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
			method: "agarwals.reconciliation.step.transform.process",
			args: {
				args: {"type":"claimbook","step_id":""}
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
	process_writeback: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.transform.process",
			args: {
				args: {"type":"writeback","step_id":""}
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {
					frappe.msgprint("writeback are loaded")
				}
			}
		})
	},

	process_writeoff: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.transform.process",
			args: {
				args: {"type":"writeoff","step_id":""}
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {
					frappe.msgprint("writeoff are loaded")
				}
			}
		})
	},

	process_settlement_staging: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.transform.process",
			args: {
				args: {"type":"Settlement","step_id":"","queue":"long"}
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
	process_writeback_jv: function (frm) {
		frappe.call({
			method: "agarwals.utils.writeback_writeoff.create_writeback_jv",
			args: {
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {

					frappe.msgprint("writeback process completed successfully")
				}
			}
		})
	},
	process_writeoff_jv: function (frm) {
		frappe.call({
			method: "agarwals.utils.writeback_writeoff.create_writeoff_jv",
			args: {
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {
					frappe.msgprint("writeoff process completed successfully")

				}
			}
		})
	},
	process_transaction_staging: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.transform.process",
			args: {
				args: {"type":"transaction","step_id":""}
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
	process_bulk_bank_transaction: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.transform.process",
			args: {
				args: {"type":"bank_transaction","step_id":""}
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
	update_index: function (frm) {
		frappe.call({
			method: "agarwals.utils.index_update.update_index",
		})
	},
	create_sales_invoice: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.sales_invoice_creator.process",
			args: {
				args: {"step_id":"","chunk_size":frm.doc.payment_matching_chunk_size,"queue":"long"}
			},
		})
	},
	mapping_insurance: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.insurance_tagger.process",
			args: {
				args: {"doctype":"Bank Transaction Staging", "step_id":"", "chunk_size":frm.doc.payment_matching_chunk_size, "queue":"long"}
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
			method: "agarwals.reconciliation.step.transcation_creator.process",
			args: {
				args: {"tag": "Credit Payment","step_id":"","chunk_size":frm.doc.payment_matching_chunk_size,"queue":"long"}
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
			method: "agarwals.reconciliation.step.claim_key_mapper.process",
			args: {
				args: {"step_id":"","chunk_size":frm.doc.payment_matching_chunk_size, "queue":"long"}
			},
		})
	},
	process_matcher: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.matcher.process",
			args: {
				args: {"step_id":"","chunk_size":frm.doc.payment_matching_chunk_size, "queue":"long"}
			},
		})
	},
	process_payment_using_payment_entry: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.payment_entry_creator.process",
			args: {
				args: {"step_id":"","chunk_size":frm.doc.payment_matching_chunk_size, "queue":"long"}
			},
		})
	},
	process_rounding_off: function (frm) {
		frappe.call({
			method: "agarwals.utils.rounding_off_process.run",
			args: {
				"_chunk_size": 100,
			}
		})
	},
	process_settlement_advice: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.advice_downloader.process",
			args: {
				args: {"step_id":"","chunk_size":frm.doc.payment_matching_chunk_size, "queue":"long"}
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
	},
	mapping_payer: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.payer_match.process",
			args: {
				args: {"step_id":"","chunk_size":frm.doc.payment_matching_chunk_size, "queue":"long"}
			},
		})
	},
	process_adjustment: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.adjust_bill.process",
			args: {
				args: {"step_id":"","chunk_size":frm.doc.payment_matching_chunk_size, "queue":"long"}
			},
		})
	},
	process_bill_adjustment: function (frm) {
		frappe.call({
			method: "agarwals.reconciliation.step.transform.process",
			args: {
				args: {"type":"adjustment","step_id":""}
			},
			callback: function (r) {
				if (r.message != "Success") {
					frappe.throw(r.message)
				}
				else {
					frappe.msgprint("Bill Adjustments are loaded")
				}
			}
		})
	},
});
