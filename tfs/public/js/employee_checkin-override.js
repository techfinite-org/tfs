// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.provide("frappe.utils.utils");

// Your Leaflet code here

frappe.ui.form.on('Employee Checkin', {

    refresh: function (frm) {
        console.log("\n\n\n\n\n\n\n ****************** employee_checkin-override **************** \n\n\n\n\n\n\n")
        // Add a custom button to the form
		showLocationOnMap(frm);
    }
});

function showLocationOnMap(frm) {
    var map = frm.get_field("custom_my_location").map;
    var latitude = frm.doc.custom_employee_latitude;
    var longitude = frm.doc.custom_employee_longitude;

    if (!isNaN(latitude) && !isNaN(longitude)) {
        var latlng = L.latLng(latitude, longitude);
        var marker = L.marker(latlng);

        map.flyTo(latlng, map.getZoom());
        marker.addTo(map);
        marker.bindPopup('Employee Location').openPopup();
    } else {
        // frappe.msgprint(__('Invalid coordinates. Please set a valid location.'));
        console.log("Invalid coordinates. Please set a valid location.")
    }
}
