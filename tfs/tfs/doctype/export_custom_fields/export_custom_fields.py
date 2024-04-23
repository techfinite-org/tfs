# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class ExportCustomFields(Document):
    pass


# @frappe.whitelist()
# def get_fields_of_doctype(doctype):
#     fields_info = []
    # exported_fields = frappe.get_all('All Export Fields', 
    #                                  filters={"exported_doctype": doctype}, 
    #                                  fields='exported_fields',
    #                                  order_by="idx")
#     extra_labels = []  # List to store extra labels

#     if exported_fields:
#         exported_labels = [ex['exported_fields'] for ex in exported_fields]

        
#         # Function to recursively fetch fields from child tables
#         def get_fields_from_table(table):
#             for field in table.fields:
#                 if field.fieldtype not in ["Section Break", "Column Break", "Table MultiSelect", "Table", "Tab Break"]:
#                     field_info = {
#                         "fieldname": field.fieldname,
#                         "fieldtype": field.fieldtype,
#                         "label": field.label
#                     }
#                     fields_info.append(field_info)

#             # Recursively fetch fields from child tables
#             for child_table in table.get("fields", {"fieldtype": "Table"}):
#                 get_fields_from_table(frappe.get_meta(child_table.options))

#         # Fetch fields from the main doctype
#         meta = frappe.get_meta(doctype)
#         for field in meta.fields:
#             if field.fieldtype not in ["Section Break", "Column Break", "Table MultiSelect", "Table", "Tab Break"]:
#                 field_info = {
#                     "fieldname": field.fieldname,
#                     "fieldtype": field.fieldtype,
#                     "label": field.label
#                 }
#                 fields_info.append(field_info)

#         # Fetch fields from child tables
#         for child_table in meta.get("fields", {"fieldtype": "Table"}):
#             get_fields_from_table(frappe.get_meta(child_table.options))

#         # Compare labels and store differences
#         for ex_label in exported_labels:
#             if ex_label not in [field_info['label'] for field_info in fields_info]:
#                 extra_labels.append(ex_label)

#         # Append extra labels to exported_fields list
#         for label in extra_labels:
#             exported_fields.append({"exported_fields": label})

#         return fields_info
#     else:
#         # If no exported_fields found, return all fields_info
#         return fields_info

def get_doc_record(doctype, name):
    return frappe.get_doc(doctype, name)
    
def add_to_child_table(fields, name):
    doc_record = get_doc_record('Export Custom Fields', name)
    for field in fields:
        doc_record.append('all_export_fields', field)
    doc_record.save()

@frappe.whitelist()
def get_fields_of_doctype(parent):
    
    export_fields = frappe.get_all('All Export Fields', 
                                     filters={'parent': parent}, 
                                     fields=['exported_fields','exported_doctype','check'],
                                     order_by="idx")

    print("-----------------parent-------------", parent)
    meta = frappe.get_meta(parent)
    print("------------------meta--------------------", meta)
    fields = []

    if not export_fields:
        total_fields = get_main_doctype_fields(parent)
        print("---------------------total_fields----------------",total_fields)
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
                print("Field not in export_fields:", field['exported_fields'])  # Print the field here
                field_dict = {
                    "exported_fields": field['exported_fields'],
                    "exported_label": field['exported_label'],
                    "check": 0,
                    "exported_doctype": parent
                }
                export_fields.append(field_dict)
                print("Field appended to export_fields:", field['exported_fields'])  # Print the appended field
            else:
                print("Field already in export_fields:", field['exported_fields'])

    return export_fields

@frappe.whitelist()
def get_exported_checked_fields(doctype):
    # Fetch exported_fields from the "All Export Fields" table where exported_doctype matches the provided doctype and check equals 1
    exported_fields = frappe.get_all('All Export Fields', filters={"exported_doctype": doctype, "check": 1}, fields='exported_fields')
    return [field.get('exported_fields') for field in exported_fields]


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
        #    print("----------------------------fields----------------------",fields)
    for child_table in meta.get("fields", {"fieldtype": "Table"}):
        child_meta = frappe.get_meta(frappe.get_meta(child_table.options).name)
        fields.extend(get_main_doctype_fields(child_meta.name))
        # print("----------------------------fields----------------------",fields)
    return fields           
           
