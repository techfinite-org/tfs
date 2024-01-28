# Copyright (c) 2023, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
import os
import pdfplumber
import json
import pandas as pd
from datetime import datetime
from frappe.model.document import Document

# class PdfExtract(Document):
@frappe.whitelist()
def pdfwithtext():
	transaction_number = 0
	customer_name = []
	folder = frappe.get_all("File", filters={"folder":"Home/Attachments"},fields=["file_url", "file_name" , "file_type"])
	customer_list  = frappe.get_all("Pdf Parser",{},["tpa_name","customer","mapping"])
	for every_customer in customer_list:
		customer_name.append(every_customer.tpa_name)
	for every_file in folder:
		if every_file.file_type ==None or every_file.file_type.lower() != "pdf":
			continue
		text = None
		base_path = os.getcwd()
		site_path =frappe.get_site_path()[1:]
		full_path = base_path+site_path
		pdf_file = full_path+str(every_file.file_url)
		pdffileobj = open(pdf_file, 'rb')
		pdfreader = pdfplumber.open(pdffileobj)
		x = len(pdfreader.pages)
		for i in range(x):
			page_obj = pdfreader.pages[i]
			if text != None:
				text += page_obj.extract_text()
			else:
				text = page_obj.extract_text()
		cleaned_words = new_line(text)
		splitted_words = cleaned_words.split(' ')		
		cleaned_words = list(filter(None, splitted_words))
		#print(cleaned_words , "\n" ,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< THE END >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		for every_customer_name in customer_name:
			if every_customer_name in text:
				tpa_name = every_customer_name
				if "TPA" in tpa_name:
					customer = tpa_name
				else:
					customer = tpa_name

		tpa_doc = frappe.get_doc("Pdf Parser",{"tpa_name":customer},["mapping"])
		tpa_json = tpa_doc.mapping
		data = json.loads(tpa_json)
		json_data = {}
		for key, values in data.items():
			if key == "name":
				json_data["name"] = [customer]
			elif key == "claim_number":
				claim_number = transaction(cleaned_words,data, values["search"] ,values["index"])
				# add_none(values, claim_number, customer)
				json_data["claim_number"] = [claim_number]
			elif key == "settled_amount":
				settled_amount = transaction(cleaned_words,data, values["search"] ,values["index"])
				# add_none(values, settled_amount, customer)
				json_data["settled_amount"] = [settled_amount]
			elif key == "utr":
				transaction_number = transaction(cleaned_words,data, values["search"] ,values["index"])
				# add_none(values, transaction_number, customer)
				json_data["utr_number"] = [transaction_number]
			elif key == "tds":
				tds = transaction(cleaned_words,data, values["search"] ,values["index"],)
				# add_none(values, tds, customer)
				json_data["tds_amount"] = [tds]
			elif key == "deductions":
				deductions = transaction(cleaned_words,data, values["search"] ,values["index"])
				# add_none(values, deductions, customer)
				json_data["deduction"] = [deductions]
		
		print(claim_number, settled_amount, transaction_number, tds, deductions)
		data_frame = pd.DataFrame(json_data)
		today = datetime.now()
		formatted_date = today.strftime("%d-%m-%Y")
		data_frame.to_csv(f"{full_path}/public/files/{customer}-{settled_amount}-{formatted_date}.csv", index=False)

	
def transaction(cleaned_words,data,word,number,trigger_word_2 = None):
		result = 0

		trigger_word = word
		trigger_position = number
		if trigger_word in cleaned_words:
			if trigger_word_2:
				result = cleaned_words[cleaned_words.index(trigger_word) and cleaned_words.index(trigger_word_2) + trigger_position]
			else:
				result = cleaned_words[cleaned_words.index(trigger_word) + trigger_position]
		if result:
			return result
		else:
			return "Null"


def add_none(values, variable, customer):
	if customer == "Aditya Birla Health Insurance Co. Limited" and values["search"]== "TDS":
		amount = []
		un_processed_variable = variable
		new_variable = un_processed_variable.split(".")
		variable = new_variable[1]
 
	if values["search"] == "None":
		variable = None
		return variable
	else:
		variable = values["search"]
		return variable
@frappe.whitelist()
def new_line(text):
	new_line = None
	for char in text:
		if char == ("\n" or "\r"):
			if new_line == None:
				new_line = " "
			else:
				new_line += " "
			continue
		else:
			if new_line == None:
				new_line = "".join(char)
			else:
				new_line += "".join(char)

	return new_line
