frappe.ui.form.on('Export Fields', {
    fetch: function(frm) {
        frappe_call(frm);
    }
});

function frappe_call(frm) {
    frappe.call({
        method:  'tfs.tfs.doctype.export_fields.export_fields.get_fields_of_doctype',
        args: {
            parent: frm.doc.export_doctype,
        },
		async:false,
        callback: function(response) {
            if (response.message) {
				// window.location.reload()
                var result = response.message;
                console.log("--------------------result------------------------", result);
                
                // // Clear existing rows in the child table
                frm.clear_table("all_export_fields");

                // Add rows to the child table
                result.forEach(function(field) {
                    var row = frappe.model.add_child(frm.doc, "All Export Fields", "all_export_fields");
                    row.label = field.exported_label; // Use 'exported_label' instead of 'fieldname'
                    row.fieldtype = field.exported_fields; // Use 'exported_fields' instead of 'fieldtype'
                    row.check = field.check;
                    row.exported_fields = field.exported_fields;
                    row.exported_doctype = frm.doc.export_doctype;
                });

                // Refresh the child table
                frm.refresh_field("all_export_fields");
            }
        }
    });
}
