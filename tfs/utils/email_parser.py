import frappe
from bs4 import BeautifulSoup
from tfs.tfs.doctype.pdf_extract.pdf_extract import get_tpa_name,get_sa_values,new_line,pdfwithtext
from agarwals.utils.error_handler import log_error
import pandas as pd
import os
from datetime import datetime

@frappe.whitelist()
def email_parsing():
    a = 'settled amount'
    b = 'utr'

    try:
        #initialize
        _base_path,_site_path,full_path,customer_name,today = _init()
        #get_email_documents
        email_to_parse = get_parsing_email()
        for email in email_to_parse:
            email = frappe.get_doc("Communication", email.name)
            #converting html to text
            soup = BeautifulSoup(email.content,features="lxml")
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text = new_line(text)
            #check whether email contains credentials
            if a and b in email.content.lower():
                #parsing
                customer_list = frappe.get_all("Email Parser", {}, ["tpa_name", "customer", "mapping"])
                for every_customer in customer_list:
                    customer_name.append(every_customer.tpa_name)
                customer = get_tpa_name(customer_name, text)
                json_data = get_sa_values(customer, text)
                settled_amount = json_data["settled_amount"]
                data_frame = pd.DataFrame(json_data)
                formatted_date = today
                data_frame.to_csv(f"{full_path}/public/files/'ep'-{customer}-{settled_amount}-{formatted_date}.csv", index=False)

            else:
                pdfwithtext(email.name)
    except Exception as e:
        log_error(e,"email_parsing","test")

def _init():
    base_path = os.getcwd()
    site_path = frappe.get_site_path()[1:]
    full_path = base_path + site_path
    customer_name = []
    today = datetime.now()
    return base_path,site_path,full_path,customer_name,today


def get_parsing_email():
    email_to_parse = []
    inclusion_text = ["ECS PAYMENT DONE"]
    last_synced_time = frappe.get_doc("Last email sync date", "last_sync")
    email_list = frappe.get_all("Communication", {"created_date": [">"[last_synced_time]]})
    for email in email_list:
        for text in inclusion_text:
            if text in email.subject:
                email_to_parse.append(email)
    return email_to_parse
