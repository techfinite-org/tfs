# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AgarwalsDashboard(Document):
	pass
# @frappe.whitelist()
# def refresh():
#     base_total = frappe.db.sql("""select sum(base_total) as base_total from `tabSales Invoice` where coalesce(`tabSales Invoice`.`status`, '') != 'Cancelled'""")
#     deposit = frappe.db.sql("""select sum(deposit) as deposit from `tabBank Transaction` where coalesce(`tabBank Transaction`.`creation`, '0001-01-01 00:00:00.000000') < '2024-02-04 01:41:12.310417'""")
#     unallocated_amt = frappe.db.sql("""select sum(unallocated_amount) as unallocated_amount from `tabBank Transaction` where coalesce(`tabBank Transaction`.`creation`, '0001-01-01 00:00:00.000000') < '2024-02-04 11:29:23.059460') stats""")
#     return base_total ,deposit, unallocated_amt

@frappe.whitelist()
def base_total():
    base_total = frappe.db.sql("""select sum(base_total) as base_total from `tabSales Invoice` where  coalesce(`tabSales Invoice`.`status`, '') != 'Cancelled'""")[0][0]
    return base_total




def get_region():
    current_user = frappe.session.user
    if current_user != "Administrator":
        current_user_doc = frappe.db.get_all("User Permission",{"user":current_user}, ["for_value"])
        if current_user_doc:
            current_user_doc = current_user_doc[0]
            region = current_user_doc.get("for_value")
        else:
            region = "All"
            
    else:
        region = "All"
        
    return region


def formatted_value(doc, key):
    match key:
        case "revenue":
            value = doc.revenue
        case "collection":
            value = doc.collection
        case "settled_amount":
            value = doc.settled_amount
        case "tds_amount":
            value = doc.tds_amount
        case "open_receipt":
            value = doc.open_receipt
        case "open_bills":
            value = doc.open_bills
        
        
    if len(str(value)) < 6:
        return round(value , 2)
    elif 6<len(str(value))<8:
        lacks_val = round((value/100000) , 2)
        return f"{lacks_val} Lacks"
    elif 8 < len(str(value)):
        cr_val = round((value/10000000), 2)
        return f"{cr_val} Cr"
    
    
@frappe.whitelist()  
def revenue():
    region = get_region()
    doc = frappe.get_doc("Agarwals Dashboard", region)
    # return str(round(doc.revenue))
    revenue = formatted_value(doc , "revenue")
    return revenue
    
@frappe.whitelist()
def collection():
    region = get_region()
    doc = frappe.get_doc("Agarwals Dashboard", region)
    collection = formatted_value(doc, "collection")
    return collection

@frappe.whitelist()
def settled_amount():
    region = get_region()
    doc = frappe.get_doc("Agarwals Dashboard", region)
    setlled_amount = formatted_value(doc, "settled_amount")
    return setlled_amount

@frappe.whitelist()
def tds_amount():
    region = get_region()
    doc = frappe.get_doc("Agarwals Dashboard", region)
    tds_amount = formatted_value(doc, "tds_amount")
    return tds_amount

@frappe.whitelist()
def open_receipt():
    region = get_region()
    doc = frappe.get_doc("Agarwals Dashboard", region)
    open_receipt = formatted_value(doc, "open_receipt")
    return open_receipt

@frappe.whitelist()
def open_bills():
    region = get_region()
    doc = frappe.get_doc("Agarwals Dashboard", region)
    open_bills = formatted_value(doc, "open_bills")
    return open_bills
    
   
@frappe.whitelist()        
def value_updater():
    region_list = frappe.db.get_all("Region")
    region_list = [each.name for each in region_list]
    region_list.append("All")
    pre_exist_region = frappe.db.get_all("Agarwals Dashboard")
    existing_region_list  = [existing_region.name for existing_region in pre_exist_region]
    for every_region in region_list:
        if every_region == "All":
            revenue = frappe.db.sql("""select sum(base_total) as base_total from `tabSales Invoice` where coalesce(`tabSales Invoice`.`status`) != 'Cancelled'""")
            collection = frappe.db.sql("""select sum(deposit) as deposit from `tabBank Transaction`""")
            open_receipt = frappe.db.sql("""select sum(unallocated_amount) as unallocated_amount from `tabBank Transaction`""")
            settled_amount = frappe.db.sql("""select sum(credit) as result from `tabGL Entry` where `tabGL Entry`.`account` = 'Debtors - A' and coalesce(`tabGL Entry`.`voucher_no`, '') not like '%%-TDS%%' and `tabGL Entry`.`voucher_type` = 'Journal Entry'""")
            tds_amount = frappe.db.sql("""select sum(debit) as result from `tabGL Entry` where `tabGL Entry`.`account` = 'TDS Credits - A'""")
            open_bills = frappe.db.sql("""select sum(total_outstanding_amount) as result from `tabSales Invoice` where coalesce(`tabSales Invoice`.`status`) != 'Cancelled'""")
        else:
            revenue = frappe.db.sql("""select sum(base_total) as base_total from `tabSales Invoice` where coalesce(`tabSales Invoice`.`status`) != 'Cancelled' AND region = %s""", every_region)
            collection = frappe.db.sql("""select sum(deposit) as deposit from `tabBank Transaction` where custom_region = %s  """, every_region)
            open_receipt = frappe.db.sql("""select sum(unallocated_amount) as unallocated_amount from `tabBank Transaction` Where  custom_region = %s""", every_region)
            settled_amount = frappe.db.sql("""select sum(credit) as result from `tabGL Entry` where `tabGL Entry`.`account` = 'Debtors - A' and region = %s AND coalesce(`tabGL Entry`.`voucher_no`, '') not like '%%-TDS%%' and `tabGL Entry`.`voucher_type` = 'Journal Entry'""", every_region)
            tds_amount = frappe.db.sql("""select sum(debit) as result from `tabGL Entry` where `tabGL Entry`.`account` = 'TDS Credits - A' AND region = %s """, every_region)
            open_bills = frappe.db.sql("""select sum(total_outstanding_amount) as result from `tabSales Invoice` where coalesce(`tabSales Invoice`.`status`) != 'Cancelled' AND region = %s""", every_region)

        if every_region not in  existing_region_list:
            doc = frappe.new_doc("Agarwals Dashboard")
        else:
            doc = frappe.get_doc("Agarwals Dashboard",every_region)
        if doc:
            doc.revenue = revenue[0][0]
            doc.collection = collection[0][0]
            doc.settled_amount = settled_amount[0][0]
            doc.tds_amount = tds_amount[0][0]
            doc.open_receipt = open_receipt[0][0]
            doc.open_bills = open_bills[0][0]
            doc.region = every_region[0][0]
            doc.save()
