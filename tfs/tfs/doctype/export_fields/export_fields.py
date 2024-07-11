# Copyright (c) 2024, Techfinite Systems and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
class ExportFields(Document):
    pass


import frappe


import frappe

@frappe.whitelist()
def get_defualt_export_field(doctype):

    is_defualt_doc = frappe.db.get_list(
        "Export Fields",
        filters={"custom_default": 1,"export_doctype":doctype},
        pluck="name"
    )
    print("is_defualt_doc", is_defualt_doc)

    if is_defualt_doc:
        # Assuming you want to return the first document found
        doc_name = is_defualt_doc[0]
        doc = frappe.get_doc("Export Fields", doc_name)
        return doc.name
    else:
        return "select_mandatory"



@frappe.whitelist()
def validate_defualt(current_doc):
    is_defualt_doc = frappe.db.sql(f"SELECT name FROM `tabExport Fields` WHERE custom_default = 1 and export_doctype = '{current_doc}' ",pluck='name')
    if is_defualt_doc:
        for doc_name in is_defualt_doc:
            doc = frappe.get_doc('Export Fields',doc_name)
            doc.custom_default = 0
            doc.save()
            frappe.db.commit()

        return 'Success'
    else:
        return 'Success'


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
    print("----------------------------doctype-------------------------",doctype)
    # Fetch all records matching the filters
    exported_fields = frappe.get_all('All Export Fields', 
                                     filters={"parent":doctype, "check": 1},
                                     fields=['exported_fields', 'index'])

    # Sort the records by custom_index, prioritizing custom_index == 1
    sorted_fields = sorted(exported_fields, key=lambda x: (x['index'] != 0, x['index']))
    # Extract the 'exported_fields' from the sorted records
    result = [field['exported_fields'] for field in sorted_fields]
    print("-------------------------------result-----------------------------",result)
    
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


@frappe.whitelist()
def get_export_field_name(doctype):
    exported_fields = frappe.get_all('Export Fields', filters={'export_doctype': doctype}, fields=['name'])
    field_names = [field['name'] for field in exported_fields]
    print("--------------------------------exported_fields---------------------------------", field_names)
    return field_names




           
