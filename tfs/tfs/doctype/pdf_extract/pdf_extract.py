# Copyright (c) 2023, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
import os
import pdfplumber
import json
import pandas as pd
from datetime import datetime
import re
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
        if "Denial"  in cleaned_words:
            continue
        print(cleaned_words)
        for every_customer_name in customer_name:
            if every_customer_name in text:
                tpa_name = every_customer_name
                if "TPA" in tpa_name:
                    customer = tpa_name
                else:
                    customer = tpa_name

        tpa_list  = frappe.db.get_all("Pdf Parser",{"tpa_name":customer, "is_enabled":True},["mapping", "index_data","name"])
        if tpa_list:
            tpa_doc = tpa_list[0]
            tpa_json = tpa_doc.mapping
            index_data = tpa_doc.index_data
            grouping_index = json.loads(index_data)
            matched_text = re.search (tpa_json,cleaned_words)
            json_data = {}
            #for Customer
            json_data["name"] = [tpa_doc.name]
            #for Claim Number
            if grouping_index["claim_number"] != 0:
                json_data["claim_number"] = matched_text.group(grouping_index["claim_number"])
            else:
                json_data["claim_number"] = None
            #for Claim Amount
            if grouping_index["claim_amount"] != 0:
                json_data["claim_amount"] = matched_text.group(grouping_index["claim_amount"])
            else:
                json_data["claim_amount"] = None
            #for deductions
            if grouping_index["deduction"] != 0:
                json_data["deduction"] = matched_text.group(grouping_index["deduction"])
            else:
                json_data["deduction"] = None
            #for tds_amount
            if grouping_index["tds_amount"] != 0:
                json_data["tds_amount"] = matched_text.group(grouping_index["tds_amount"])
            else:
                json_data["tds_amount"] = None
            #for Settled Amount
            if grouping_index["settled_amount"] != 0:
                json_data["settled_amount"] = matched_text.group(grouping_index["settled_amount"])
            else:
                json_data["settled_amount"] = None
            #for Utr number
            if grouping_index["utr_number"] != 0:
                json_data["utr_number"] = matched_text.group(grouping_index["utr_number"])
            else:
                json_data["utr_number"] = None
            #for Transaction date
            if grouping_index["transaction_date"] != 0:
                json_data["transaction_date"] = matched_text.group(grouping_index["transaction_date"])
            else:
                json_data["transaction_date"] = None
            #for Parsed Date 
            json_data["parsed_date"] = datetime.now()
            
            #saving it to csv
            data_frame = pd.DataFrame(json_data)
            today = datetime.now()
            formatted_date = today.strftime("%d-%m-%Y")
            data_frame.to_csv(f"{full_path}/public/files/{tpa_doc.name}-{formatted_date}.csv", index=False)
        else:
            frappe.throw("There is no corresponding tpa name in the pdf parser doctype")
        
        
    

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
