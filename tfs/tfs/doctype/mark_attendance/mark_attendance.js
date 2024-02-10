frappe.ui.form.on('Mark Attendance', {
    refresh: function (frm) {
        // // Style customization
        // frm.fields_dict.select_all.$input.css({
        //     'font-size': '13px',
        //     'text-align': 'center',
        //     'background-color': '#42a5fc',
        //     'color': 'white',
        //     'display': 'inline-block',
        // });

        // frm.fields_dict.unselect_all.$input.css({
        //     'font-size': '13px',
        //     'text-align': 'center',
        //     'background-color': '#42a5fc',
        //     'color': 'white',
        //     'display': 'inline-block',
        // });

        // Custom button to mark attendance
        frm.add_custom_button(__('Mark Attendance'), function () {
            setDateInShiftType(frm);
            markAttendanceSelectedShifts(frm);
           
        });

        // Call your custom function on page load/refresh
        frappe_call(frm);
    },

    // Function to handle the list of unmarked employees
        show_unmarked_shift: function (frm, unmarked_shifts) {
            const $wrapper = frm.get_field("shift_html").$wrapper;
            $wrapper.empty();
            const shift_wrapper = $(`<div class="shift_wrapper">`).appendTo($wrapper);

            frm.employees_multicheck = frappe.ui.form.make_control({
                parent: shift_wrapper,
                df: {
                    fieldname: "shift_multicheck",  
                    fieldtype: "MultiCheck",
                    select_all: true,
                    columns: 4,
                    get_data: () => {
                        return unmarked_shifts.map((shift) => {
                            return {
                                label: `${shift}`,
                                value: shift,
                                checked: 0,
                            };
                        });
                    },
                },
                render_input: true,
            });

            frm.shift_multicheck.refresh_input();
        },

   
});




// Function to make frappe call and populate unmarked employees
function frappe_call(frm) {
    frappe.call({
        method: 'tfs.tfs.doctype.mark_attendance.mark_attendance.get_all_shift',
        args: {
            // Add any necessary arguments here
        },
    }).then((r) => {
        if (r.message && r.message.length > 0) {
            var system_result = r.message
            console.log("shift console:",system_result)
            frm.events.show_unmarked_shift(frm, r.message);
        }
    });
}

// Function to mark attendance for selected shifts
function markAttendanceSelectedShifts(frm) {
   
    const marked_shifts = frm.employees_multicheck.get_checked_options();
    console.log("marked_shifts",marked_shifts)
    frappe.call({
        method: 'tfs.shift_type_override.process_auto_attendance_for_all_shifts',
        args: {
            shift_list: marked_shifts,
        },
        freeze: true,
        freeze_message: __("Marking Attendance")
        
        // callback: function (response) {
        //     console.log("Response message:", response.message);
        //     var responseLength = response.message.length;
        //     if (response.message && typeof response.message === 'object' && Object.keys(response.message).length > 0) {
        //         Object.keys(response.message).forEach(function (shift) {
        //             frappe.msgprint(response.message[shift]);
        //         });
        //     }
        // }
    }).then((r) => {
        if (!r.exc) {
            frappe.show_alert({ message: __("Attendance marked successfully"), indicator: "green" });
            frm.refresh();
        }
    });
}

// Function to update shift type dates
function setDateInShiftType(frm) {
    var from_date = frm.doc.process_attendance_after;
    var to_date = frm.doc.last_sync_of_checkin;
    
    frappe.call({
        method: 'tfs.tfs.doctype.mark_attendance.mark_attendance.update_shift_type_dates',
        args: {
            process_attendance_after: from_date,
            last_sync_of_checkin: to_date,
        },
        // async: false,
        callback: function (response) {
            console.log("Response message:", response.message);
        }
    });
}


