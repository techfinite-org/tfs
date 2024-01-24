// Load Leaflet library if not already loaded
// if (typeof L === 'undefined') {
//     // Assuming 'assets/frappe/js/lib/leaflet/leaflet.js' is the correct path
//     frappe.require('assets/frappe/js/lib/leaflet/leaflet.js', function() {
//         initializeLeaflet();
        
//     });
// } else {
//     initializeLeaflet();
// }



frappe.ui.form.on('Employee Checkin', {
    refresh: function (frm) {
        console.log("\n\n\n\n\n\n\n ****************** employee_checkin-override **************** \n\n\n\n\n\n\n")
        // Add a custom button to the form
        showLocationOnMap(frm);
    }
});

function initializeLeaflet() {
    frappe.provide("frappe.utils.utils");

    frappe.ui.form.on('Employee Checkin', {
        refresh: function (frm) {
            showLocationOnMap(frm);
        }
    });
}

function showLocationOnMap(frm) {
    var map = frm.get_field("custom_my_location").map;
    var latitude = frm.doc.custom_employee_latitude;
    var longitude = frm.doc.custom_employee_longitude;

    if (!isNaN(latitude) && !isNaN(longitude)) {
        var latlng = new L.LatLng(latitude, longitude);
        var marker = L.marker(latlng);
         
        map.flyTo(latlng, map.getZoom());
        marker.addTo(map);
        marker.bindPopup('Employee Location').openPopup();
    } else {
        console.log("Invalid coordinates. Please set a valid location.")
    }
}
