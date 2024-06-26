# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bs4 import BeautifulSoup
from tfs.tfs.doctype.pdf_extract.pdf_extract import get_tpa_name,get_sa_values,new_line,pdfwithtext,is_folder_exist,create_file_doc, create_fileupload,process_dataframe
from agarwals.utils.error_handler import log_error
import pandas as pd
import os
from datetime import datetime
import sys

class EmailExtract(Document):
	pass

@frappe.whitelist()
def email_parsing():
	doc = None
	claim_no = "Transaction Reference"
	customer = None
	i=1 #for checking the null cut off email eg: Not needed char -- needed char -- needed char then  it will use this to return continue
	a=1 # this is used to get the exact count of i after i changed to  continue
	b=0 # this is used to name the file
	data_frame = pd.DataFrame()
	try:
		#initialize
		_base_path,_site_path,full_path,customer_name,today = _init()
		#get_email_documents
		email_to_parse,last_synced_time = get_parsing_email()
		if email_to_parse != None:
			for email in email_to_parse:
				b+=1
				#converting html to text
				control_panel = frappe.get_single('Control Panel')
				content_texts = frappe.get_all("Inclusion Email Text",{"type":"Content"})
				if content_texts:
					for content_text in content_texts:
						if  content_text.lower() in email.text_content.lower():
							email_contents = email.text_content
							type = "text_content"
							break
						else:
							email_contents = email.content
							type = "html"
				else:
					email_contents = email.content
					type = "html"
					content_text = None
				try:
					email_contents = email_contents.split(control_panel.dlimitter)
					with_delimitter = True
				except:
					email_contents = email_contents
					with_delimitter = False
				if type == "text_content" and with_delimitter == False:
					text = email_contents
					text = new_line(text)
					if text:
					#check whether email contains credentials
						i,a,data_frame,customer = text_parsing(content_text,text,customer_name, full_path,today, doc,control_panel,email,i,a,data_frame,customer)
						if i == 0:
							break
				else:
					for email_content in email_contents:
						if type =="html":
							soup = BeautifulSoup(email_content,features="lxml")
							for script in soup(["script", "style"]):
								script.extract()
							text = soup.get_text()
							lines = (line.strip() for line in text.splitlines())
							chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
							text = '\n'.join(chunk for chunk in chunks if chunk)
							text = new_line(text)
							i,a,data_frame,customer = text_parsing(content_text,text,customer_name, full_path,today, doc,control_panel,email,i,a,data_frame,customer)
							if i == 0:
								break
							elif i == "continue":
								i = a
								a = 1
								continue
						else:
							text = new_line(email_content)
							if text:
							#check whether email contains credentials
								i,a,data_frame,customer = text_parsing(content_text,text,customer_name, full_path,today, doc,control_panel,email,i,a,data_frame,customer)
								if i == 0:
									break
								elif i == "continue":
									i = a
									a = 1
									continue
					if data_frame.claim_number.size:
						original_customer_name = frappe.get_all("Email Parser",{"tpa_name":customer},pluck= "customer")[0]
						is_folder_exist(f"{full_path}/private/files/EyeFoundation/Email Extract")
						full_file_path = f"{full_path}/private/files/EyeFoundation/Email Extract/ep-{original_customer_name}-{str(b)}-{str(i)}.csv"
						file_path = f"/private/files/EyeFoundation/Email Extract/ep-{original_customer_name}-{str(b)}-{str(i)}.csv"
						#file creation
						data_frame.to_csv(full_file_path, index=False)
						file_url = create_file_doc(full_file_path, file_path)
						create_fileupload(file_url,doc,original_customer_name, today)
						control_panel.last_sync_datetime = today
						control_panel.save()
	except Exception as e:
		log_error(e)



def text_parsing(content_text,text,customer_name, full_path,today, doc,control_panel,email,i,a,data_frame,customer):
		if content_text != None and content_text.lower() in text.lower() :
			#parsing
			customer_list = frappe.get_all("Email Parser",{},["*"])
			for every_customer in customer_list:
				customer_name.append(every_customer.tpa_name)
			customer = get_tpa_name(customer_name, text)
			if customer:
				json_data = get_sa_values(customer, text,"Email Parser")
				settled_amount = json_data["settled_amount"][0]
				data_frame = process_dataframe(json_data,data_frame)
				#file path
				i+=1
				return i,a,data_frame,customer
			else:
				parsed_text_update(text,"Email")
				frappe.msgprint("No customer detected")
				return False
		elif email.has_attachment:
			pdfwithtext(email.name)
			control_panel.last_sync_datetime = today
			control_panel.save()
		else:
			i = "continue"
			a = 1
			return i,a,data_frame,customer
		
def _init():
	base_path = os.getcwd()
	site_path = frappe.get_site_path()[1:]
	full_path = base_path + site_path
	customer_name = []
	today = datetime.now()
	return base_path,site_path,full_path,customer_name,today


def get_parsing_email():
	email_to_parse = []
	inclusion_text = frappe.get_all("Inclusion Email Text",{},pluck="name")#settlement advice email patterns
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


def parsed_text_update(text, type):
    parsed_doc = frappe.get_single("Parsed Text")
    if type == "Email":
        parsed_doc.email_text = text
    else:
        parsed_doc.pdf_text = text
    parsed_doc.save()
    
    