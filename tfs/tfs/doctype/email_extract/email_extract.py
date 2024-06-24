# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bs4 import BeautifulSoup
from tfs.tfs.doctype.pdf_extract.pdf_extract import get_tpa_name,get_sa_values,new_line,pdfwithtext
from agarwals.utils.error_handler import log_error
import pandas as pd
import os
from datetime import datetime

class EmailExtract(Document):
	pass

@frappe.whitelist()
def email_parsing():
	settled_amount = 'Amount (INR)'
	utr = 'UTR no.'
	claim_no = "claim_no"

	try:
		#initialize
		_base_path,_site_path,full_path,customer_name,today = _init()
		#get_email_documents
		email_to_parse,last_synced_time = get_parsing_email()
		if email_to_parse != None:
			for email in email_to_parse:
				#converting html to text
				control_panel = frappe.get_single('Control Panel')
				try:
					email_contents = email.content.split(control_panel.dlimitter)
				except:
					email_contents = email.content
				for email_content in email_contents:
					soup = BeautifulSoup(email_content,features="lxml")
					for script in soup(["script", "style"]):
						script.extract()
					text = soup.get_text()
					lines = (line.strip() for line in text.splitlines())
					chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
					text = '\n'.join(chunk for chunk in chunks if chunk)
					text = new_line(text)
					if text:
					#check whether email contains credentials
						if settled_amount.lower() and utr.lower() and claim_no in text.lower():
							#parsing
							customer_list = frappe.get_all("Email Parser", {}, ["*"])
							for every_customer in customer_list:
								customer_name.append(every_customer.tpa_name)
							customer = get_tpa_name(customer_name, text)
							json_data = get_sa_values(customer, text,"Email Parser")
							settled_amount = json_data["settled_amount"][0]
							data_frame = pd.DataFrame(json_data)
							formatted_date = today
							data_frame.to_csv(f"{full_path}/public/files/'ep'-{customer}-{settled_amount}-{formatted_date}.csv", index=False)
							last_synced_time.last_sync_datetime = today
							last_synced_time.save()

						else:
							pdfwithtext(email.name)
					else:
						continue
	except Exception as e:
		log_error(e)



def _init():
	base_path = os.getcwd()
	site_path = frappe.get_site_path()[1:]
	full_path = base_path + site_path
	customer_name = []
	today = datetime.now()
	return base_path,site_path,full_path,customer_name,today


def get_parsing_email():
	email_to_parse = []
	inclusion_text = frappe.get_all("Inclusion Email Text",{},pluck="name")
	control_panel = frappe.get_single('Control Panel')
	email_list = frappe.get_all("Communication", filters = {"creation": [">",control_panel.last_sync_datetime], "email_account":control_panel.recipients},fields = ["*"])
	if email_list:
		#the below code can also be written like this
		#email_to_parse = [email for email in email_list if (text in email.subject for text in inclusion_text)]
		for email in email_list:
			for text in inclusion_text:
				if text in email.subject:
					email_to_parse.append(email)
					continue
		return email_to_parse,control_panel.last_sync_datetime
	else:
		return None