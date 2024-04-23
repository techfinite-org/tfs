frappe.ui.form.on('Export Field', {
    export_doctype: function(frm) {
        var selected_doctype = frm.doc.export_doctype;
        frm.events.show_unmarked_fields(frm, selected_doctype);
    },
    show_unmarked_fields: function(frm, selected_doctype) {
        // Fetch fields of the selected doctype
        var fields = [];

        // Fetch fields of the main doctype
        frappe.model.with_doctype(selected_doctype, function() {
            // Fetch fields of the main doctype
            fields = frappe.meta.get_docfields(selected_doctype)
                .filter(df => df && df.fieldtype !== "Section Break" && 
                               df.fieldtype !== "Tab Break" && 
                               df.fieldtype !== "Column Break" &&
                               !df.hidden);
            
            // Fetch fields of child tables
            var child_tables = frappe.meta.get_table_fields(selected_doctype);
            var field_html = '';
            
            // Generate checkboxes for each field of the main doctype
            var mainDoctypeColumnCount = 4;
            var mainDoctypeRowCount = Math.ceil(fields.length / mainDoctypeColumnCount);
            for (var i = 0; i < mainDoctypeRowCount; i++) {
                field_html += '<div class="row">';
                for (var j = 0; j < mainDoctypeColumnCount; j++) {
                    var index = i * mainDoctypeColumnCount + j;
                    if (index >= fields.length) {
                        break;
                    }
                    var field = fields[index];
                    var isMandatory = field.reqd ? 'color: red;' : '';
                    field_html += `<div class="col-md-3" style="${isMandatory}"><input type="checkbox" name="${field.fieldname}" value="${field.fieldname}"> ${field.label}</div>`;
                }
                field_html += '</div>';
            }
            
            // Generate checkboxes for each field in child tables
            child_tables.forEach(function(child_table) {
                var child_fields = frappe.meta.get_docfields(child_table.options)
                    .filter(df => df && df.fieldtype !== "Section Break" && 
                                      df.fieldtype !== "Tab Break" && 
                                      df.fieldtype !== "Column Break" &&
                                      !df.hidden);
                
                // Add heading for child table
                field_html += `<div><strong>${child_table.label}</strong></div>`;
                
                var childTableColumnCount = 4;
                var childTableRowCount = Math.ceil(child_fields.length / childTableColumnCount);
                for (var i = 0; i < childTableRowCount; i++) {
                    field_html += '<div class="row">';
                    for (var j = 0; j < childTableColumnCount; j++) {
                        var index = i * childTableColumnCount + j;
                        if (index >= child_fields.length) {
                            break;
                        }
                        var child_field = child_fields[index];
                        var isMandatory = child_field.reqd ? 'color: red;' : '';
                        field_html += `<div class="col-md-3" style="${isMandatory}"><input type="checkbox" name="${child_field.fieldname}" value="${child_field.fieldname}"> ${child_field.label}</div>`;
                    }
                    field_html += '</div>';
                }
            });

            // Clear previous checkboxes
            frm.fields_dict["export_html"].$wrapper.empty();

            // Append new checkboxes
            frm.fields_dict["export_html"].$wrapper.append(field_html);
        });
    },

    save_checked_values: function(frm) {
        var checked_values = [];
        var unchecked_values = [];
        // Iterate through each checkbox input within export_html field and store checked values
        frm.fields_dict["export_html"].$wrapper.find('input[type="checkbox"]').each(function() {
            var fieldname = $(this).attr('name');
            var value = $(this).is(':checked');
            if (value) {
                checked_values.push(fieldname);
            } else {
                unchecked_values.push(fieldname);
            }
        });

        // Save checked and unchecked values to the database
        frm.doc.exported_check_and_unchecked_fields = {
            checked: checked_values,
            unchecked: unchecked_values
        };
        frm.save();
    }
});

frappe.ui.form.on('Export Field', {
    save: function(frm) {
        frm.events.save_checked_values(frm);
    }
});
