import frappe
import os
import pdfplumber
import json
import pandas as pd
from datetime import datetime
import re
from frappe.model.document import Document

@frappe.whitelist()
def pdf_bt_extract():
    folder = frappe.get_all("File", filters={"folder":"Home/Attachments"},fields=["file_url", "file_name" , "file_type"])
    for every_file in folder:
        file_name = every_file.file_name
        if every_file.file_type ==None or every_file.file_type.lower() != "pdf":
            continue
        
        text = None
        base_path = os.getcwd()
        site_path =frappe.get_site_path()[1:]
        full_path = base_path+site_path
        pdf_file = full_path+"/public"+str(every_file.file_url)
        pdffileobj = open(pdf_file, 'rb')
        pdfreader = pdfplumber.open(pdffileobj)
        x = len(pdfreader.pages)
        for i in range(x):
            page_obj = pdfreader.pages[i]
            if text != None:
                text += page_obj.extract_text()
            else:
                text = page_obj.extract_text()
        space_removed_text = new_line(text)
    
        splitted_text = space_removed_text.split("------------------------------------------------------------------------------------------------------------------------------------")
        current_row = 1
        last_append_row = 3
        cleaned_list = []
        for each_section in splitted_text:
            if current_row <= 3  or current_row == int(last_append_row)+4:
                cleaned_list.append(each_section)
                if current_row > 6 :
                    last_append_row = current_row
            current_row += 1
        
        string_text = " ".join(cleaned_list)
        # pattern =r"(\d+-\d+-\d+)(.*?)(?=\d+-\d+-\d+|$)"
        pattern =r"\d{2}-\d{2}-\d{4}.*?(?=\d{2}-\d{2}-\d{4}|$)"
        json_data = {"transactions" : []}
        ordered_texts = re.findall(pattern, string_text)
        b = 0
        sno = 1
        for ordered_text in ordered_texts:
            b+=1
            withdrawl_pattern = r"([\d-]+) ([a-zA-Z ]+) (\d+) ([0-9,.]+) ([0-9,.A-z]+) .*"
            deposit_pattern = r"(\d{2}-\d{2}-\d{4}) (.*) ([0-9.,]+) ([0-9,.]+Cr).*"
            sms_pattern = r"(\d{2}-\d{2}-\d{4}) (.*) ([0-9.,]+) ([0-9,.]+Cr).*"
            if b>3:  
                splitted_text = ordered_text.split(" ")
                a = 0 
                
                if "Collecting" in splitted_text:
                    try:
                        pattern_matching = re.findall(withdrawl_pattern, ordered_text)
                        if pattern_matching:
                            transaction = {
                            "sno" : sno,
                            "date" : pattern_matching[0][0],
                            "transaction_details" : pattern_matching[0][1],
                            "cheque_no" : pattern_matching[0][2],
                            "withdrawl_amount" : pattern_matching[0][3],
                            "balance" :  pattern_matching[0][4]
                            }
                            sno +=1
                        json_data["transactions"].append(transaction)
                    except Exception as e:
                        print("it is not a withdrawl pattern", e)
        
                elif "Sender" or "VIJAYAWADA,MACHAVARAM" in splitted_text:
                        try:
                            pattern_matching =  re.findall(deposit_pattern, ordered_text)
                            if pattern_matching:
                                transaction = {
                                "sno" : sno,
                                "date" : pattern_matching[0][0],
                                "transaction_details" : pattern_matching[0][1],
                                "deposit_amount" : pattern_matching[0][2],
                                "balance" : pattern_matching[0][3]
                                }
                                sno +=1
                                for splitup in splitted_text:
                                    a += 1
                                    if "Number" in splitup:
                                        transaction["utr_number"] = splitted_text[a]
                                            
                                    elif "Account" in splitup:
                                        transaction["sender_account"] = splitted_text[a]
                                    elif "IFSC" in splitup:
                                        transaction["sender_ifsc"] = splitted_text[a]
                                json_data["transactions"].append(transaction)
                        except Exception as e:
                            print("it is not a deposit pattern", e)
                            
                
                elif "Sms" in splitted_text:
                    try:
                        pattern_matching =  re.findall(sms_pattern, ordered_text)
                        if pattern_matching:
                            transaction ={
                            "sno" : sno,
                            "date" : pattern_matching[0][0],
                            "transaction_details" : pattern_matching[0][1],
                            "deposit_amount" : pattern_matching[0][2],
                            "balance" : pattern_matching[0][3]
                            }
                            sno += 1
                            json_data["transactions"].append(transaction)
                    except Exception as e:
                            print("it is not a sms pattern", e)                  
                            
                    print("this does not match any pattern", ordered_text)
                            
        data_frame = pd.DataFrame(json_data["transactions"])
        today = datetime.now()
        formatted_date = today.strftime("%d-%m-%Y")
        data_frame.to_csv(f"{full_path}/public/files/{file_name}-bank_transaction-{formatted_date}.csv", index = False)

        
        
        
        
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