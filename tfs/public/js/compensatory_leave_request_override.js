// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Compensatory Leave Request', {
	refresh: function(frm) {
        console.log("\n\n\n\n\n\n\n ****************** Compensatory Leave Request override **************** \n\n\n\n\n\n\n")
		frm.set_query("leave_type", function() {
			return {
				filters: {
					"is_compensatory": true
				}
			};
		});
	},
	half_day: function(frm) {
		if(frm.doc.half_day == 1){
			frm.set_df_property('half_day_date', 'reqd', true);
		}
		else{
			frm.set_df_property('half_day_date', 'reqd', false);
		}
	},
	custom_work_from_date_time: function(frm){
        if(!frm.doc.work_from_date){
            frm.set_value("work_from_date", frm.doc.custom_work_from_date_time);
        }

    },
    custom_work_end_date_time: function(frm){
        if(!frm.doc.work_end_date){
            frm.set_value("work_end_date", frm.doc.custom_work_end_date_time);
        }

    },
	leave_type: function(frm) {
        // show_date_time_field(frm)
        console.log("leave_type changed:", frm.doc.leave_type);
        frm.set_value("work_from_date", null);
        frm.set_value("work_end_date", null);
        frm.set_value("custom_work_from_date_time", null);
        frm.set_value("custom_work_end_date_time", null);
        show_date_time_field(frm);
    },
	onload: function(frm) {
        // // Ignore cancellation of doctype on cancel all.
        frm.toggle_display('custom_work_from_date_time', false);
        frm.toggle_display('custom_work_end_date_time', false);

        if (frm.doc.custom_work_from_date_time && frm.doc.custom_work_end_date_time) {

            frm.toggle_display('custom_work_from_date_time', true);
            frm.toggle_display('custom_work_end_date_time',true);
            frm.toggle_display('work_from_date', false);
            frm.toggle_display('work_end_date',false);
        }
       
	}
});

function show_date_time_field(frm) {
    frappe.call({
        method: 'tfs.compensatory_leave_request_overrides.hide_unhide_date_time_field',
        args: {
            leave_type: frm.doc.leave_type
        },
        callback: function (response) {
            if (response.message) {
                console.log("------------------------- response message -----------------------------", response.message);
    
                var result = response.message;
                if (frm.doc.leave_type && result == 1) {
                    frm.toggle_display('custom_work_from_date_time', true);
                    frm.toggle_display('custom_work_end_date_time', true);
                    frm.toggle_display('work_from_date', false);
                    frm.toggle_display('work_end_date', false);
					frm.toggle_display('half_day',false);
                } else if (frm.doc.leave_type && result == 'hide') {
                    frm.toggle_display('work_from_date', true);
                    frm.toggle_display('work_end_date', true);
                    frm.toggle_display('custom_work_from_date_time', false);
                    frm.toggle_display('custom_work_end_date_time', false);
                }
            }
        }
    });
}

