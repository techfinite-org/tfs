frappe.ui.form.on('Mark Attendance', {
   
    refresh: function (frm) {

        frm.fields_dict.select_all.$input.css({
            'font-size': '13px',
            'text-align': 'center',
            'background-color': '#42a5fc',
            'color': 'white',
            'display': 'inline-block',  // Changed from 'block' to 'inline-block'
        });
        
        frm.fields_dict.unselect_all.$input.css({
            'font-size': '13px',
            'text-align': 'center',
            'background-color': '#42a5fc',
            'color': 'white',
            'display': 'inline-block',  // Changed from 'block' to 'inline-block'
        });
        $('<style>')
        .prop('type', 'text/css')
        .html('@media (min-width: 576px) {.col-sm-6 {flex: 0 0 15.6666666667%; max-width: 15.6666666667%; }}')
        .appendTo('head');


        cur_frm.cscript.select_all = function(doc) {
            selectAllCheckboxes(frm)
                    
            }

            cur_frm.cscript.unselect_all = function(doc) {
                unselectAllCheckboxes(frm)
                          
                } 

        // Call your custom function on page load/refresh
        frappe_call(frm);

        // Add a custom button
        frm.add_custom_button(__('Mark Attendance'), function () {
            setDateInShiftType(frm);
            markAttendanceSelectedShifts(frm);
        });
    }
});

function frappe_call(frm) {
    frappe.call({
        method: 'tfs.tfs.doctype.mark_attendance.mark_attendance.get_all_shift',
        args: {
            // Add any necessary arguments here
        },
        callback: function (response) {
            try {
                if (response.message && Array.isArray(response.message)) {
                    console.log("Response message:", response.message);

                    // Log the entire array as a JSON string
                    console.log("Result:", JSON.stringify(response.message));

                    // Clear existing rows in 'Shift Collection' child table
                    frm.clear_table('shift_collection');

                    // Add fetched shifts to 'Shift Collection' child table
                    response.message.forEach(function (item) {
                        // Check if the shift is not already in the child table
                        if (!isShiftInTable(frm, item)) {
                            var _row = frappe.model.add_child(frm.doc, 'Shift Collection', 'shift_collection');
                            frappe.model.set_value(_row.doctype, _row.name, 'shift', item);
                        }
                    });

                    // Refresh the 'Shift Collection' child table
                    frm.refresh_field('shift_collection');
                }
            } catch (error) {
                console.error("Error processing response:", error);
            }
        }
    });
}

function isShiftInTable(frm, shift) {
    var shiftCollection = frm.doc.shift_collection || [];
    for (var i = 0; i < shiftCollection.length; i++) {
        if (shiftCollection[i].shift === shift) {
            return true;
        }
    }
    return false;
}

function markAttendanceSelectedShifts(frm) {
    var shiftCollection = frm.doc.shift_collection || [];
    var selectedShifts = [];

    // Iterate through the 'Shift Collection' child table
    for (var i = 0; i < shiftCollection.length; i++) {
        var row = shiftCollection[i];
        if (row.select) {
            selectedShifts.push(row.shift);
        }
    }

    console.log("selectedShifts", selectedShifts);

    frappe.call({
        // method: 'hrms.hr.doctype.shift_type.shift_type.process_auto_attendance_for_all_shifts',
        method: 'tfs.shift_type_override.process_auto_attendance_for_all_shifts',
        args: {
            shift_list: selectedShifts,  // Pass the array directly
        },
        callback: function (response) {
            console.log("Response message:", response.message);
        }
    });
}

function setDateInShiftType(frm) {
    var from_date = frm.doc.process_attendance_after;
    var to_date = frm.doc.last_sync_of_checkin;

    frappe.call({
        method: 'tfs.tfs.doctype.mark_attendance.mark_attendance.update_shift_type_dates',
        args: {
            process_attendance_after: from_date,
            last_sync_of_checkin: to_date,
        },
        callback: function (response) {
            console.log("Response message:", response.message);
        }
    });
}

function selectAllCheckboxes(frm) {
    // Iterate through the 'Shift Collection' child table and select all checkboxes
    var shiftCollection = frm.doc.shift_collection || [];
    for (var i = 0; i < shiftCollection.length; i++) {
        frappe.model.set_value(shiftCollection[i].doctype, shiftCollection[i].name, 'select', 1);
    }

    // Refresh the 'Shift Collection' child table
    frm.refresh_field('shift_collection');
}

function unselectAllCheckboxes(frm) {
    // Iterate through the 'Shift Collection' child table and unselect all checkboxes
    var shiftCollection = frm.doc.shift_collection || [];
    for (var i = 0; i < shiftCollection.length; i++) {
        frappe.model.set_value(shiftCollection[i].doctype, shiftCollection[i].name, 'select', 0);
    }

    // Refresh the 'Shift Collection' child table
    frm.refresh_field('shift_collection');
}
