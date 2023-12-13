var longitude;
var latitude;

frappe.ui.form.on('Employee Checkin Page', {
    
    onload_post_render: function (frm) {
        // Customize the style of the "in" button
        frm.page.clear_primary_action();
        
        
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

        // // Customize the style of the "out" button
        // frm.fields_dict.out.$input.css({
        //     'font-size': '16px',
        //     'text-align': 'center',
        //     'background-color': '#42a5fc',
        //     'color': 'white',
        //     'height': '40px',
        //     'width': '150px',
        //     'margin': '0 auto',
        //     'display': 'block'
        // });





// Initialize the current state
var currentState = 'IN';

// Add a function to be executed when the button is pressed
frm.fields_dict.in.$input.on('click', function () {
   
    function onPositionRecieved(position){
        longitude= position.coords.longitude;
        latitude= position.coords.latitude;
        frm.set_value('longitude',longitude);
        frm.set_value('latitude',latitude);
        console.log(longitude);
        console.log(latitude);
        fetch('https://api.opencagedata.com/geocode/v1/json?q='+latitude+'+'+longitude+'&key=de1bf3be66b546b89645e500ec3a3a28')
         .then(response => response.json())
        .then(data => {
            var city=data['results'][0].components.city;
            var state=data['results'][0].components.state;
            var area=data['results'][0].components.residential;
            frm.set_value('city',city);
            frm.set_value('state',state);
            frm.set_value('area',area);
            console.log(data);
            frappe_call(currentState);
            currentState = currentState === 'IN' ? 'OUT' : 'IN';
            frm.fields_dict.in.$input.val(currentState);
            // Update the button label using inner text (assuming it's a button type field)
            frm.fields_dict.in.$input[0].innerText = currentState;
        })

        .catch(err => console.log(err));
        frm.set_df_property('my_location','options','<div class="mapouter"><div class="gmap_canvas"><iframe width=100% height="300" id="gmap_canvas" src="https://maps.google.com/maps?q='+latitude+','+longitude+'&t=&z=17&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe><a href="https://yt2.org/youtube-to-mp3-ALeKk00qEW0sxByTDSpzaRvl8WxdMAeMytQ1611842368056QMMlSYKLwAsWUsAfLipqwCA2ahUKEwiikKDe5L7uAhVFCuwKHUuFBoYQ8tMDegUAQCSAQCYAQCqAQdnd3Mtd2l6"></a><br><style>.mapouter{position:relative;text-align:right;height:300px;width:100%;}</style><style>.gmap_canvas {overflow:hidden;background:none!important;height:300px;width:100%;}</style></div></div>');
        frm.refresh_field('my_location');
    }
    
    function locationNotRecieved(positionError){
        console.log(positionError);
    }
    
    // if(frm.doc.longitude && frm.doc.latitude){
    //     frm.set_df_property('my_location','options','<div class="mapouter"><div class="gmap_canvas"><iframe width=100% height="300" id="gmap_canvas" src="https://maps.google.com/maps?q='+frm.doc.latitude+','+frm.doc.longitude+'&t=&z=17&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe><a href="https://yt2.org/youtube-to-mp3-ALeKk00qEW0sxByTDSpzaRvl8WxdMAeMytQ1611842368056QMMlSYKLwAsWUsAfLipqwCA2ahUKEwiikKDe5L7uAhVFCuwKHUuFBoYQ8tMDegUAQCSAQCYAQCqAQdnd3Mtd2l6"></a><br><style>.mapouter{position:relative;text-align:right;height:300px;width:100%;}</style><style>.gmap_canvas {overflow:hidden;background:none!important;height:300px;width:100%;}</style></div></div>');
    //     frm.refresh_field('my_location');
    // } else {
        if(navigator.geolocation){
            navigator.geolocation.getCurrentPosition(onPositionRecieved,locationNotRecieved,{ enableHighAccuracy: true});
        }
    
    // Toggle between 'IN' and 'OUT'
 
    // Log the current state (optional)
    console.log("Current state:", currentState);

    // Call your frappe_call function with the current state
  

    // Update the button value
    
    // If the button label is stored in a data attribute, you can update it like this:
    // frm.fields_dict.in.$input.attr('data-label', currentState);

 

});





        function frappe_call(buttonName) {
            frappe.call({
                method: 'tfs.tfs.doctype.employee_checkin_page.employee_checkin_page.employee_check_in',
                args: {
                    log_type: buttonName,
                    emp_longitude: longitude,
                    emp_latitude: latitude
                },
                callback: function (response) {
                    if (response.message) {
                        // Optionally handle the response here
                        console.log(response.message);
                        // Set the rounded distance_in_km in the form document
                        // frm.set_value('distance_in_km', Math.round(response.message));
                        frm.set_value('distance_in_km', parseFloat(response.message).toFixed(2));

                    }
                }
            });
        }
    },

    
});
