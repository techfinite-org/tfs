// Copyright (c) 2023, Techfinite Systems and contributors
// For license information, please see license.txt

 frappe.ui.form.on("Data Import Mapping", {
 	mapping_doctype:function(frm) {
 	        frappe.model.with_doctype(frm.doc.mapping_doctype, function () {
                var fields = frappe.get_meta(frm.doc.mapping_doctype).fields;
                var columns_in_doctype = []
                fields.forEach(function(field) {
                    if(field.fieldtype !== "Section Break" && field.fieldtype !== "Column Break" && field.fieldtype !== "Tab Break"){
                        columns_in_doctype.push({'column_in_doctype':field.fieldname});
                    }
                });
                frm.set_value('mapping_columns',columns_in_doctype)
            });
        }
 });