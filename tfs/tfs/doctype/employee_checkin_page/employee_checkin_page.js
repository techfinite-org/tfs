var longitude;
var latitude;
var result;

frappe.ui.form.on('Employee Checkin Page', {
    onload_post_render: function (frm) {
        frm.disable_save();

        frm.fields_dict.in.$input.css({
            'font-size': '16px',
            'text-align': 'center',
            'background-color': '#42a5fc',
            'color': 'white',
            'height': '40px',
            'width': '150px',
            'margin': '40px auto 100px',  // Added margin at the bottom
            'display': 'block',
        });

        frm.fields_dict.out.$input.css({
            'font-size': '16px',
            'text-align': 'center',
            'background-color': '#42a5fc',
            'color': 'white',
            'height': '40px',
            'width': '150px',
            'margin': '10px auto 0',  // Added margin at the top
            'display': 'block',
        });

        function handleButtonClick(logType) {
            function onPositionReceived(position) {
                longitude = position.coords.longitude;
                latitude = position.coords.latitude;
                frm.set_value('longitude', longitude);
                frm.set_value('latitude', latitude);
                console.log("-----------------------------------", longitude);
                console.log(latitude);

                // Disable the buttons for 10 seconds
                disableButtons();

                // Play the click sound
                playClickSound();

                // Set the log_type dynamically based on the button clicked
                frappe_call(logType, frm); // Pass frm as a parameter
            }

            function locationNotReceived(positionError) {
                console.log(positionError);
            }

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(onPositionReceived, locationNotReceived, { enableHighAccuracy: true });
            }

            console.log("Current state:", logType);
        }

        function disableButtons() {
            frm.fields_dict.in.$input.prop('disabled', true);
            frm.fields_dict.out.$input.prop('disabled', true);

            setTimeout(function () {
                frm.fields_dict.in.$input.prop('disabled', false);
                frm.fields_dict.out.$input.prop('disabled', false);
            }, 5000); // Enable buttons after 5 seconds
        }

        function playClickSound() {
            // Play the click sound
            frappe.utils.play_sound('submit'); // Replace 'path_to_your_click_sound.mp3' with the actual path to your sound file
        }

        frm.fields_dict.in.$input.on('click', function () {
            handleButtonClick('IN');
        });

        frm.fields_dict.out.$input.on('click', function () {
            handleButtonClick('OUT');
        });
    },
});



function playClickSound() {
    // Play the click sound
    frappe.utils.play_sound('submit'); // Replace 'path_to_your_click_sound.mp3' with the actual path to your sound file
}
// Function to handle the callback and set the button value
function frappe_call(logType, frm) { // Add frm as a parameter
    frappe.call({
        method: 'tfs.tfs.doctype.employee_checkin_page.employee_checkin_page.employee_check_in',
        args: {
            log_type: logType,
            emp_longitude: longitude,
            emp_latitude: latitude
        },
        callback: function (response) {
            if (response.message) {
                console.log("------------------------- response message -----------------------------", response.message);
                console.log("------------------------- this array value -----------------------------", response.message[1]);
                result = response.message;
                frm.set_value('distance_in_km', parseFloat(result[0]).toFixed(2));
                console.log("checkin",result[2]);
                if (result[2]) {
                    let itemShow = [].concat(result[2]);
                    showLocationDialog(itemShow, logType, frm); // Pass frm as a parameter
                }
            }
        }
    });
}

function showLocationDialog(itemShow, logType, frm) { // Add frm as a parameter
    let d = new frappe.ui.Dialog({
        title: 'Enter details',
        fields: [
            {
                label: 'Please select your Sign In Location ',
                fieldname: 'Location',
                fieldtype: 'Select',
                options: itemShow
            },
            // Add other fields as needed
        ],
        primary_action_label: 'Submit',
        primary_action(values) {
            console.log(values);
            frappe.call({
                method: 'tfs.tfs.doctype.employee_checkin_page.employee_checkin_page.employee_check_in_remote_location',
                args: {
                    log_type: logType,
                    emp_longitude: longitude,
                    emp_latitude: latitude,
                    device_id: values
                },
                callback: function (r) {
                    console.log(r.message)
                    playClickSound()
                }
            });

            d.hide();
        }
    });

    d.show();
}

// Function to show location on the map (if needed)
function showLocationOnMap(frm, longitude, latitude) {
    // Your code to show location on the map
}
