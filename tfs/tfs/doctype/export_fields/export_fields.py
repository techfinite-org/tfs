# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
class ExportFields(Document):
    pass
@frappe.whitelist()
def get_fields_of_doctype(parent):
    
    export_fields = frappe.get_all('All Export Fields', 
                                     filters={'parent': parent}, 
                                     fields=['exported_fields','exported_doctype','check','index'],
                                     order_by="idx")
    if not export_fields:
        total_fields = get_main_doctype_fields(parent)
        return total_fields
    else:
        total_fields = get_main_doctype_fields(parent)
        for field in total_fields:
            found = False
            for export_field in export_fields:
                if field['exported_fields'] == export_field['exported_fields']:
                    found = True
                    break
            if not found:
                field_dict = {
                    "exported_fields": field['exported_fields'],
                    "exported_label": field['exported_label'],
                    "check": 0,
                    "exported_doctype": parent
                    }
                export_fields.append(field_dict)
    return export_fields

# @frappe.whitelist()
# def get_exported_checked_fields(doctype):
#     exported_fields = frappe.get_all('All Export Fields', filters={"exported_doctype": doctype, "check": 1}, fields=['exported_fields','custom_index'])
#     return [field.get('exported_fields') for field in exported_fields]

@frappe.whitelist()
def get_exported_checked_fields(doctype):
    # Fetch all records matching the filters
    exported_fields = frappe.get_all('All Export Fields', 
                                     filters={"exported_doctype": doctype, "check": 1}, 
                                     fields=['exported_fields', 'index'])

    # Sort the records by custom_index, prioritizing custom_index == 1
    sorted_fields = sorted(exported_fields, key=lambda x: (x['index'] != 0, x['index']))
    # Extract the 'exported_fields' from the sorted records
    result = [field['exported_fields'] for field in sorted_fields]
    
    return result

@frappe.whitelist()
def get_main_doctype_fields(parent):
    meta = frappe.get_meta(parent)
    fields = []
    for field in meta.fields:
        if field.fieldtype not in ["Section Break", "Column Break", "Table MultiSelect", "Table", "Tab Break"]:
           field_dict = {
                    "exported_label": field.fieldname,
                    "exported_fields":field.label,
                    "check": 0,
                    "exported_doctype": parent
                }
           fields.append(field_dict)
    for child_table in meta.get("fields", {"fieldtype": "Table"}):
        child_meta = frappe.get_meta(frappe.get_meta(child_table.options).name)
        fields.extend(get_main_doctype_fields(child_meta.name))
    return fields           
           
