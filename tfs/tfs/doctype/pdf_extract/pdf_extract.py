# Copyright (c) 2023, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
import os
import pdfplumber
import json
import pandas as pd
from datetime import datetime
import re
from agarwals.utils.error_handler import log_error
from frappe.model.document import Document

# class PdfExtract(Document):
@frappe.whitelist()
def pdfwithtext(parent_name = None):
    customer_name = []
    folder = file_list(parent_name)
    if folder:
        customer_list = frappe.get_all("Pdf Parser",{},["tpa_name","customer","mapping"])
        for every_customer in customer_list:
            customer_name.append(every_customer.tpa_name)
        for every_file in folder:
            if every_file.file_type == None or every_file.file_type.lower() != "pdf":
                continue
            text = None
            base_path = os.getcwd()
            site_path = frappe.get_site_path()[1:]
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
            if "Denial" in cleaned_words:
                continue

            customer = get_tpa_name(customer_name, cleaned_words)
            json_data = get_sa_values(customer, cleaned_words,"Pdf Parser")
            settled_amount = json_data["settled_amount"][0]
            if settled_amount:
                data_frame = pd.DataFrame(json_data)
                today = datetime.now()
                formatted_date = today
                data_frame.to_csv(f"{full_path}/public/files/pp-{customer}-{settled_amount}-{formatted_date}.csv", index=False)
            else:
                log_error("no_settled_amount")
    else:
        log_error("no_pdf_to_parse")

def file_list(parent_name):
    if parent_name:
        folder = frappe.get_all("File", {"attached_to_name": parent_name}, ["file_url", "file_name", "file_type"])
    else:
        folder = frappe.get_all("File", filters={"folder": "Home/Attachments"}, fields=["file_url", "file_name", "file_type"])
    return folder
        
        
def pattern(word):
    pattern = r'\b' + re.escape(word) + r'\s+(\w+)'
    return pattern

def match(word, position, cleaned_words):
    match = re.search(word,cleaned_words)
    split_pos = str(position).split(",")
    for pos in split_pos:
        if match:
            result = match.group(int(pos))
            if result:
                return result
            else:
                log_error("there are no result for this match")
        else:
            log_error("There are no match for this pattern")


@frappe.whitelist()
def new_line(text):
    new_line = None
    for char in text:
        if char == ("\n" or "\r"):
            if new_line == None:
                new_line = " "
            else:
                new_line += " "
        else:
            if new_line == None:
                new_line = "".join(char)
            else:
                new_line += "".join(char)

    return new_line


def get_tpa_name(customer_name, text):
    try:
        for every_customer_name in customer_name:
            if every_customer_name in text:
                tpa_name = every_customer_name
                customer = tpa_name
                return customer
    except Exception as e:
        log_error(e)



def get_sa_values(customer, cleaned_words,doctype):
    try:
        tpa_doc = frappe.get_doc(doctype, {"tpa_name": customer}, ["mapping"])
        tpa_json = tpa_doc.mapping
        data = json.loads(tpa_json)
        json_data = {}
        json_data["name"] = [customer]
        for key, values in data.items():
            if key == "claim_number":
                claim_number = match(values["search"], values["index"], cleaned_words)
                json_data["claim_number"] = [claim_number]
            elif key == "settled_amount":
                settled_amount = match(values["search"], values["index"], cleaned_words)
                settled_amount = remove_comma(settled_amount)
                json_data["settled_amount"] = [int(settled_amount)]
            elif key == "utr":
                transaction_number = match(values["search"], values["index"], cleaned_words)
                json_data["utr_number"] = [transaction_number]
            elif key == "tds":
                tds = match(values["search"], values["index"], cleaned_words)
                tds = remove_comma(tds)
                json_data["tds_amount"] = [int(tds)]
            elif key == "deductions":
                deductions = match(values["search"], values["index"], cleaned_words)
                deductions = remove_comma(deductions)
                json_data["deduction"] = [int(deductions)]
        return json_data
    except Exception as e:

        log_error(e)




def remove_comma(value):
    if "," in value:
        output_value = value.replace(",", "")
    else:
        output_value = value
    return output_value