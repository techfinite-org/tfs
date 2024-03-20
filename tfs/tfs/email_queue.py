import frappe

def check_email_queue_status():
    email_queue_records = frappe.get_all("Email Queue", filters={"status": "Not Sent"}, fields=["name"])
    
    for name in email_queue_records:
        record = frappe.get_doc("Email Queue", name)
        record.send()

@frappe.whitelist()
def schedule_email_sender():
    # Schedule the check_email_queue_status function to run periodically (e.g., every 5 minutes)
    frappe.enqueue(check_email_queue_status, queue='long', timeout=600, job_name = "Email Queue")
