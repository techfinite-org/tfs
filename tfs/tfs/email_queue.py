import frappe

def check_email_queue_status():
    email_queue_records = frappe.get_all("Email Queue", filters={"status": "Not Sent"}, fields=["name"])
    
    for name in email_queue_records:
        record = frappe.get_doc("Email Queue", name)
        record.send()
        
def add_permission():
    alloc_doc = frappe.get_all("Leave Allocation",{'leave_type':'Permission Hours - Personal'},'name')
    try:
        for i in range(0,len(alloc_doc)):
            update_alloc_doc = frappe.get_doc("Leave Allocation",alloc_doc[i].name)
            update_alloc_doc.new_leaves_allocated =  update_alloc_doc.new_leaves_allocated + 90
            update_alloc_doc.save()
            frappe.db.commit()
    except Exception as e:
        print(f'{alloc_doc[i].name}  : {e}')        

@frappe.whitelist()
def schedule_permission_hours():
    # Schedule the check_email_queue_status function to run periodically (e.g., every 5 minutes)
    frappe.enqueue(add_permission, queue='long', timeout=600, job_name = "Add Permission Hours Every Month")
    
@frappe.whitelist()    
def schedule_email_sender():    
    frappe.enqueue(check_email_queue_status, queue='long', timeout=600, job_name = "Email Queue")
    
