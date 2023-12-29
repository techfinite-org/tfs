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
            'margin': '0 auto',
            'display': 'block'
        });
        frm.fields_dict.out.$input.css({
            'font-size': '16px',
            'text-align': 'center',
            'background-color': '#42a5fc',
            'color': 'white',
            'height': '40px',
            'width': '150px',
            'margin': '0 auto',
            'display': 'block'
        });

        // Function to handle button clicks
        function handleButtonClick(logType) {
            function onPositionReceived(position) {
                longitude = position.coords.longitude;
                latitude = position.coords.latitude;
                frm.set_value('longitude', longitude);
                frm.set_value('latitude', latitude);
                console.log("-----------------------------------", longitude);
                console.log(latitude);
                playClickSound();
                disableButtons();
                // Set the log_type dynamically based on the button clicked
                frappe_call(logType);
                 // Disable the buttons for 5 seconds
                
                 // Play the click sound
               
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

        // Function to handle the callback and set the button value
        function frappe_call(logType) {
            frappe.call({
                method: 'tfs.tfs.doctype.employee_checkin_page.employee_checkin_page.employee_check_in',
                args: {
                    log_type: logType,
                    emp_longitude: longitude,
                    emp_latitude: latitude
                },
                callback: function (response) {
                    if (response.message) {
                        console.log(response.message);
                        result = response.message;
                        frm.set_value('distance_in_km', parseFloat(result).toFixed(2));
                        
                        
                        // Update the button label when the response is received
                       
                    }
                }
            });
        }
    },
});
