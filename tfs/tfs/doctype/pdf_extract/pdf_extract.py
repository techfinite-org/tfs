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

class PdfExtract(Document):
    pass

@frappe.whitelist()
def pdfwithtext():
    fileupload_list_of_unparsed_pdfs = frappe.db.get_all("File upload",{"status": "Open","document_type":"Settlement Advice"},["*"])
    for file_upload_record in fileupload_list_of_unparsed_pdfs:
        # pdf = file_upload_record.upload
        customer, cleaned_words = identify_customer(file_upload_record)
        skip = validate_pdf(cleaned_words)
        if skip == True:
            continue
        if customer:
            json_data = {}
            customer_parsing_details = frappe.get_doc("Settlement Advice Pdf Configuration",customer)
            key_list = ["claim_number", "claim_amount","deduction","tds_amount","settled_amount","utr_number","transaction_date"] 
            tpa_json = customer_parsing_details.regex
            matched_text = re.search (tpa_json,cleaned_words)
            index_json = customer_parsing_details.indexes
            index_obj = json.loads(index_json)
            for key in key_list:
                json_data = extract_values(key, index_obj, json_data, matched_text)
            # pasred_obj = json.loads(json_data)
            sa_doc = create_sa(json_data, file_upload_record)
                
    
def identify_customer(file_upload_record):
        base_path = os.getcwd()
        site_path =frappe.get_site_path()[1:]
        full_path = base_path+site_path+file_upload_record.upload
    # list of customers
        customers = []
        customer_list  = frappe.db.get_all("Settlement Advice Pdf Configuration",{},["customer_search_text","customer","regex"])
        for customer in customer_list:
            customers.append(customer.customer_search_text)
            
    #Extracting pdf 
        pdffileobj = open(full_path, 'rb')
        pdfreader = pdfplumber.open(pdffileobj)
        cleaned_words = pdf_data_extract(pdfreader)
    #check customer in cleaned words
        for every_customer_name in customers:
            if every_customer_name in cleaned_words:
                tpa_name = every_customer_name
                customer_name = [customer_name_in_pdf.customer for customer_name_in_pdf in customer_list if customer_name_in_pdf.customer_search_text == tpa_name]
                break
            
        if customer_name and cleaned_words:
            return customer_name[0], cleaned_words


def validate_pdf(cleaned_words):
    words_to_check = ["Denial"]
    for word in words_to_check:
        if word in cleaned_words:
            return True

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


def pdf_data_extract(pdfreader):
    text = None
    for i in range(len(pdfreader.pages)):
            page_obj = pdfreader.pages[i]
            if text != None:
                text += page_obj.extract_text()
            else:
                text = page_obj.extract_text()
    cleaned_words = new_line(text)
    return cleaned_words
    
def extract_values(key, group_index , json_data, matched_text):
    test = group_index[key]
    if group_index[key] != 0:
        json_data[key] = matched_text.group(group_index[key])
    else:
        json_data[key] = None
    return json_data
    
def change_date_format(new_str):
    str_split = re.search('^\d+\W+(\w+)', new_str)
    try:
        month_str = str_split.group(1)
    except:
        formatted_date = re.sub("\D","-",new_str)
        return formatted_date
    i = 1
    months = ["jan","feb","mar","apr","may","june","july", "aug","sep","oct","nov","dec"]
    if month_str.lower() in  months:
        for month in months :
            if month_str.lower() == month:
                if i < 10 :
                    processed_str = re.sub('([A-Za-z]+)', "0"+str(i), new_str)
                else:
                    processed_str = re.sub('([A-Za-z]+)', str(i), new_str)
                break
            elif month == "dec":
                processed_str = new_str
            i+=1
        formatted_date = re.sub("\D","-",processed_str)
    else:
        formatted_date = re.sub("\D","-",new_str)
            
    return formatted_date 
    
def create_sa(pasred_obj,file_upload_record):
    str = pasred_obj["transaction_date"]
    new_string = change_date_format(str)
    transaction_date = datetime.strptime(new_string,"%d-%m-%Y").date()
    new_settlement_advice = frappe.new_doc("Settlement Advice")
    new_settlement_advice.claim_id = pasred_obj["claim_number"]
    new_settlement_advice.utr_number = pasred_obj["utr_number"]
    new_settlement_advice.claim_amount = pasred_obj["claim_amount"]
    new_settlement_advice.disallowed_amount = pasred_obj["deduction"]
    new_settlement_advice.tds_amount=pasred_obj["tds_amount"]
    new_settlement_advice.settled_amount = pasred_obj["settled_amount"]
    new_settlement_advice.paid_date = transaction_date
    new_settlement_advice.source_file = file_upload_record["name"]
    new_settlement_advice.status = "Open"
    new_settlement_advice.save()
    return new_settlement_advice