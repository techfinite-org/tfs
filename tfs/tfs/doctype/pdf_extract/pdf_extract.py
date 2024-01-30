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

        tpa_doc = frappe.get_doc("Pdf Parser",{"tpa_name":customer},["mapping"])
        tpa_json = tpa_doc.mapping
        data = json.loads(tpa_json)
        json_data = {}
        for key, values in data.items():
            if key == "name":
                json_data["name"] = [customer]
            elif key == "claim_number":
                claim_number = match(values["search"], values["index"], cleaned_words)
                json_data["claim_number"] = [claim_number]
            elif key == "settled_amount":
                settled_amount = match(values["search"], values["index"], cleaned_words)
                json_data["settled_amount"] = [settled_amount]
            elif key == "utr":
                transaction_number = match(values["search"], values["index"], cleaned_words)
                json_data["utr_number"] = [transaction_number]
            elif key == "tds":
                tds = match(values["search"], values["index"], cleaned_words)
                json_data["tds_amount"] = [tds]
            elif key == "deductions":
                deductions = match(values["search"], values["index"], cleaned_words)
                json_data["deduction"] = [deductions]
        
        print(claim_number, settled_amount, transaction_number, tds, deductions)
        data_frame = pd.DataFrame(json_data)
        today = datetime.now()
        formatted_date = today.strftime("%d-%m-%Y")
        data_frame.to_csv(f"{full_path}/public/files/{customer}-{settled_amount}-{formatted_date}.csv", index=False)
        
        
        
        
        
def pattern(word):
    pattern = r'\b' + re.escape(word) + r'\s+(\w+)'
    return pattern

def match(word , position , cleaned_words):
    to_search = pattern(word)
    match = re.search (to_search,cleaned_words)
    if match:
        result = match.group(position)
        if result:
            print(word ,":" ,result)
            return result
        else:
            print("there are no result for this match")
    else:
        print("There are no match for this pattern",to_search)
    

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
