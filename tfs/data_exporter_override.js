frappe.provide("frappe.data_import");

frappe.data_import.DataExporter = class DataExporter {
    constructor(doctype, exporting_for) {
        this.doctype = doctype;
        this.exporting_for = exporting_for;
        frappe.model.with_doctype(doctype, () => {
            this.make_dialog();
        });
    }

    make_dialog() {
        this.dialog = new frappe.ui.Dialog({
            title: __("Export Data"),
            fields: [
                {
                    fieldtype: "Select",
                    fieldname: "file_type",
                    label: __("File Type"),
                    options: ["Excel", "CSV"],
                    default: "CSV",
                },
                {
                    fieldtype: "Select",
                    fieldname: "export_records",
                    label: __("Export Type"),
                    options: [
                        {
                            label: __("All Records"),
                            value: "all",
                        },
                        {
                            label: __("Filtered Records"),
                            value: "by_filter",
                        },
                        {
                            label: __("5 Records"),
                            value: "5_records",
                        },
                        {
                            label: __("Blank Template"),
                            value: "blank_template",
                        },
                    ],
                    default: this.exporting_for === "Insert New Records" ? "blank_template" : "all",
                    change: () => {
                        this.update_record_count_message();
                    },
                },
                {
                    fieldtype: "HTML",
                    fieldname: "filter_area",
                    depends_on: (doc) => doc.export_records === "by_filter",
                },
                {
                    fieldtype: "Section Break",
                },
                {
                    fieldtype: "HTML",
                    fieldname: "select_all_buttons",
                },
                {
                    label: __(this.doctype),
                    fieldname: this.doctype,
                    fieldtype: "MultiCheck",
                    columns: 2,
                    on_change: () => this.update_primary_action(),
                    options: this.get_multicheck_options(this.doctype),
                },


                ...frappe.meta.get_table_fields(this.doctype).map((df) => {
                    let doctype = df.options;
                    let child_fieldname = df.fieldname;
                    let label = df.reqd
                        ? __('{0} ({1}) (1 row mandatory)', [__(df.label || df.fieldname), __(doctype)])
                        : __("{0} ({1})", [__(df.label || df.fieldname), __(doctype)]);
                    return {
                        label,
                        fieldname: child_fieldname,
                        fieldtype: "MultiCheck",
                        columns: 2,
                        on_change: () => this.update_primary_action(),
                        options: this.get_multicheck_options(doctype, child_fieldname),
                    };
                }),
            ],
            primary_action_label: __("Export"),
            primary_action: (values) => this.export_records(values),
           on_page_show: () => {
                this.initialize_export_field_selection();
            }
        });

        this.make_filter_area();
        this.make_select_all_buttons();
        this.update_record_count_message();

        this.dialog.show();
    }

    export_records(values) {
        let method = "/api/method/frappe.core.doctype.data_import.data_import.download_template";

        let multicheck_fields = this.dialog.fields
            .filter((df) => df.fieldtype === "MultiCheck")
            .map((df) => df.fieldname);

        let doctype_field_map = Object.assign({}, values);
        for (let key in doctype_field_map) {
            if (!multicheck_fields.includes(key)) {
                delete doctype_field_map[key];
            }
        }

        let filters = null;
        if (values.export_records === "by_filter") {
            filters = this.get_filters();
        }

        open_url_post(method, {
            doctype: this.doctype,
            file_type: values.file_type,
            export_records: values.export_records,
            export_fields: doctype_field_map,
            export_filters: filters,
        });
    }

    make_filter_area() {
        this.filter_group = new frappe.ui.FilterGroup({
            parent: this.dialog.get_field("filter_area").$wrapper,
            doctype: this.doctype,
            on_change: () => {
                this.update_record_count_message();
            },
        });
    }

make_select_all_buttons() {
    let for_insert = this.exporting_for === "Insert New Records";
    let section_title = for_insert
        ? __("Select Fields To Insert")
        : __("Select Fields To Update");

    let $select_all_buttons = $(`
        <div class="mb-3">
            <h6 class="form-section-heading uppercase">${section_title}</h6>
            <button class="btn btn-default btn-xs" data-action="select_all">
                ${__("Select All")}
            </button>
            ${
                for_insert
                    ? `<button class="btn btn-default btn-xs" data-action="select_mandatory">
                ${__("Select Mandatory")}
            </button>`
                    : ""
            }
            <button class="btn btn-default btn-xs" data-action="unselect_all">
                ${__("Unselect All")}
            </button>
            <!-- Link field for Export Fields -->
            <div class="position-relative">
                <input type="text" class="form-control dropdown-filter-input" placeholder="${__("Type to filter")}" data-fieldtype="Link" data-fieldname="export_field" data-options="Export Field">
                <div class="dropdown-menu mt-1 position-absolute w-100" aria-labelledby="dropdownMenuButton" style="max-height: 200px; overflow-y: auto;">
                    <!-- Dropdown items will be inserted here dynamically -->
                </div>
            </div>
        </div>
    `);

    $select_all_buttons.on("click", "[data-action='select_all']", () => this.select_all());
    $select_all_buttons.on("click", "[data-action='select_mandatory']", () => this.select_mandatory());
    $select_all_buttons.on("click", "[data-action='unselect_all']", () => this.unselect_all());

    this.dialog.get_field("select_all_buttons").$wrapper.html($select_all_buttons);

    // Fetch dropdown items when the input field is focused
    $select_all_buttons.find('.dropdown-filter-input').on('focus', () => {
        frappe.call({
            method: 'tfs.tfs.doctype.export_fields.export_fields.get_export_field_name',
            args: {
                doctype: this.doctype,
            },
            callback: (response) => {
                if (response.message) {
                    let result = response.message;
                    console.log("Received dropdown items:", result);

                    // Populate dropdown menu
                    let $dropdownMenu = $select_all_buttons.find('.dropdown-menu');
                    let $filterInput = $select_all_buttons.find('.dropdown-filter-input');

                    // Function to populate dropdown with filtered or full list
                    const populateDropdown = (items) => {
                        $dropdownMenu.empty(); // Clear existing items

                        items.forEach(item => {
                            let $dropdownItem = $(`<a class="dropdown-item" href="#" data-value="${item}">${item}</a>`);
                            $dropdownMenu.append($dropdownItem);

                            // Handle click event on dropdown item
                            $dropdownItem.click((event) => {
                                event.preventDefault();
                                $filterInput.val(item); // Place selected item in the input box
                                $dropdownMenu.hide(); // Hide the dropdown menu
                                this.dropdown(event); // Call the dropdown method if needed
                            });
                        });

                        // Show the dropdown
                        $dropdownMenu.show();
                    };

                    // Initial population of dropdown with all items
                    populateDropdown(result);

                    // Handle typing in the filter input
                    $filterInput.on('input', function() {
                        let inputValue = $(this).val().toLowerCase();

                        // Filter items based on user input
                        let filteredItems = result.filter(item => {
                            return item.toLowerCase().includes(inputValue);
                        });

                        // Update dropdown with filtered items
                        populateDropdown(filteredItems);
                    });

                    // Hide dropdown when input loses focus
                    $filterInput.on('blur', function() {
                        setTimeout(() => {
                            $dropdownMenu.hide();
                        }, 200); // Delay to allow click event on dropdown items to be registered
                    });
                } else {
                    console.log("No items received from the server.");
                }
            },
            error: (error) => {
                console.error("Error fetching dropdown items:", error);
            }
        });
    });
}

make_select_all_buttons() {
    let for_insert = this.exporting_for === "Insert New Records";
    let section_title = for_insert
        ? __("Select Fields To Insert")
        : __("Select Fields To Update");

    let $select_all_buttons = $(`
        <div class="mb-3">
            <h6 class="form-section-heading uppercase">${section_title}</h6>
            <div class="d-flex align-items-center">
                <button class="btn btn-default btn-xs mr-2" data-action="select_all">
                    ${__("Select All")}
                </button>
                ${
                    for_insert
                        ? `<button class="btn btn-default btn-xs mr-2" data-action="select_mandatory">
                    ${__("Select Mandatory")}
                </button>`
                        : ""
                }
                <button class="btn btn-default btn-xs mr-2" data-action="unselect_all">
                    ${__("Unselect All")}
                </button>
                <!-- Link field for Export Fields -->
                <div class="position-relative flex-grow-1">
                    <input type="text" class="form-control dropdown-filter-input" placeholder="${__("Export Fields")}" data-fieldtype="Link" data-fieldname="export_field" data-options="Export Field">
                    <div class="dropdown-menu mt-1 position-absolute w-100" aria-labelledby="dropdownMenuButton" style="max-height: 200px; overflow-y: auto; overflow-x: hidden; white-space: normal; word-wrap: break-word;">
                        <!-- Dropdown items will be inserted here dynamically -->
                    </div>
                </div>
            </div>
        </div>
    `);

    $select_all_buttons.on("click", "[data-action='select_all']", () => this.select_all());
    $select_all_buttons.on("click", "[data-action='select_mandatory']", () => this.select_mandatory());
    $select_all_buttons.on("click", "[data-action='unselect_all']", () => this.unselect_all());

    this.dialog.get_field("select_all_buttons").$wrapper.html($select_all_buttons);

    // Fetch dropdown items when the input field is focused
    $select_all_buttons.find('.dropdown-filter-input').on('focus', () => {
        frappe.call({
            method: 'tfs.tfs.doctype.export_fields.export_fields.get_export_field_name',
            args: {
                doctype: this.doctype,
            },
            callback: (response) => {
                if (response.message) {
                    let result = response.message;
                    console.log("Received dropdown items:", result);

                    // Populate dropdown menu
                    let $dropdownMenu = $select_all_buttons.find('.dropdown-menu');
                    let $filterInput = $select_all_buttons.find('.dropdown-filter-input');

                    // Function to populate dropdown with filtered or full list
                    const populateDropdown = (items) => {
                        $dropdownMenu.empty(); // Clear existing items

                        items.forEach(item => {
                            let $dropdownItem = $(`<a class="dropdown-item" href="#" data-value="${item}" style="white-space: normal; word-wrap: break-word;">${item}</a>`);
                            $dropdownMenu.append($dropdownItem);

                            // Handle click event on dropdown item
                            $dropdownItem.click((event) => {
                                event.preventDefault();
                                $filterInput.val(item); // Place selected item in the input box
                                $dropdownMenu.hide(); // Hide the dropdown menu
                                this.dropdown(event); // Call the dropdown method if needed
                            });
                        });

                        // Show the dropdown
                        $dropdownMenu.show();
                    };

                    // Initial population of dropdown with all items
                    populateDropdown(result);

                    // Handle typing in the filter input
                    $filterInput.on('input', function() {
                        let inputValue = $(this).val().toLowerCase();

                        // Filter items based on user input
                        let filteredItems = result.filter(item => {
                            return item.toLowerCase().includes(inputValue);
                        });

                        // Update dropdown with filtered items
                        populateDropdown(filteredItems);
                    });

                    // Hide dropdown when input loses focus
                    $filterInput.on('blur', function() {
                        setTimeout(() => {
                            $dropdownMenu.hide();
                        }, 200); // Delay to allow click event on dropdown items to be registered
                    });

                    // Handle keyboard navigation and selection
                    $filterInput.on('keydown', function(event) {
                        let $activeItem = $dropdownMenu.find('.dropdown-item.active');
                        switch (event.key) {
                            case 'ArrowDown':
                                event.preventDefault();
                                if ($activeItem.length === 0) {
                                    let $firstItem = $dropdownMenu.find('.dropdown-item:first-child');
                                    $firstItem.addClass('active');
                                    $dropdownMenu.scrollTop(0); // Scroll to the top
                                } else {
                                    let $nextItem = $activeItem.removeClass('active').next();
                                    if ($nextItem.length) {
                                        $nextItem.addClass('active');
                                        $dropdownMenu.scrollTop($dropdownMenu.scrollTop() + $nextItem.position().top);
                                    } else {
                                        $dropdownMenu.find('.dropdown-item:first-child').addClass('active');
                                        $dropdownMenu.scrollTop(0); // Scroll to the top
                                    }
                                }
                                break;
                            case 'ArrowUp':
                                event.preventDefault();
                                if ($activeItem.length === 0) {
                                    let $lastItem = $dropdownMenu.find('.dropdown-item:last-child');
                                    $lastItem.addClass('active');
                                    $dropdownMenu.scrollTop($dropdownMenu.prop("scrollHeight")); // Scroll to the bottom
                                } else {
                                    let $prevItem = $activeItem.removeClass('active').prev();
                                    if ($prevItem.length) {
                                        $prevItem.addClass('active');
                                        $dropdownMenu.scrollTop($dropdownMenu.scrollTop() + $prevItem.position().top - $dropdownMenu.height() + $prevItem.outerHeight());
                                    } else {
                                        $dropdownMenu.find('.dropdown-item:last-child').addClass('active');
                                        $dropdownMenu.scrollTop($dropdownMenu.prop("scrollHeight")); // Scroll to the bottom
                                    }
                                }
                                break;
                            case 'Enter':
                                event.preventDefault();
                                if ($activeItem.length > 0) {
                                    $activeItem.trigger('click');
                                }
                                break;
                        }
                    });
                } else {
                    console.log("No items received from the server.");
                }
            },
            error: (error) => {
                console.error("Error fetching dropdown items:", error);
            }
        });
    });
}




dropdown(event = null, selectedValue = null) {
    if (event && event.preventDefault) {
        event.preventDefault();
        selectedValue = $(event.target).data('value');
    } else if (selectedValue) {
        // Handle case when selectedValue is passed directly
        selectedValue = selectedValue;
    } else {
        console.error('No event or selected value provided');
        return;
    }

    console.log('Selected Value:', selectedValue);

    frappe.call({
        method: 'tfs.tfs.doctype.export_fields.export_fields.get_exported_checked_fields',
        args: {
            doctype: selectedValue,
        },
        callback: (response) => {
            if (response.message) {
                let result = response.message;

                // Get mandatory table fields
                let mandatory_table_fields = frappe.meta
                    .get_table_fields(this.doctype)
                    .map((df) => df.fieldname);
                mandatory_table_fields.push(this.doctype);

                // Get multi-check fields that are mandatory
                let multicheck_fields = this.dialog.fields
                    .filter((df) => df.fieldtype === "MultiCheck")
                    .map((df) => df.fieldname)
                    .filter((doctype) => mandatory_table_fields.includes(doctype));

                // Update checkboxes based on result
                let checkboxesToUpdate = [].concat(
                    ...multicheck_fields.map((fieldname) => {
                        let field = this.dialog.get_field(fieldname);

                        // Map the labels from field.options
                        const sortedResult = field.options.map(option => option.label);

                        // Initialize an array to store common labels and checkboxes
                        let commonLabelsAndCheckboxes = [];

                        // Check for common elements and valid field options
                        if (field && field.options) {
                            result.forEach(label => {
                                if (sortedResult.includes(label)) {
                                    let checkbox = field.options.find(option => option.label === label);
                                    if (checkbox && checkbox.$checkbox) {
                                        commonLabelsAndCheckboxes.push({
                                            label: label,
                                            checkbox: checkbox.$checkbox.find("input").get(0)
                                        });
                                    }
                                }
                            });

                            // Check child table fields
                            frappe.meta.get_table_fields(this.doctype).forEach(df => {
                                let cdt = df.options;
                                let child_fieldname = df.fieldname;
                                let child_multicheck = this.dialog.get_field(child_fieldname);
                                if (child_multicheck) {
                                    child_multicheck.options.forEach(option => {
                                        if (result.includes(option.label)) {
                                            option.$checkbox.find("input").prop("checked", true).trigger("change");
                                        }
                                    });
                                }
                            });
                        }

                        return commonLabelsAndCheckboxes.map(entry => entry.checkbox);
                    })
                );

                // Unselect all checkboxes before selecting new ones
                this.unselect_all();

                // Select checkboxes based on retrieved data
                $(checkboxesToUpdate.flat()).prop("checked", true).trigger("change");
            }
        }
    });

    // Update the dropdown button text with the selected value
    $('#dropdownMenuButton').text(selectedValue);

    // Add any additional logic you want to execute on dropdown selection
}

    select_all() {
        this.dialog.$wrapper.find(":checkbox").prop("checked", true).trigger("change");
    }

	select_mandatory() {
		console.log("function calling")
		let mandatory_table_fields = frappe.meta
			.get_table_fields(this.doctype)
			.filter((df) => df.reqd)
			.map((df) => df.fieldname);
		mandatory_table_fields.push(this.doctype);

		let multicheck_fields = this.dialog.fields
			.filter((df) => df.fieldtype === "MultiCheck")
			.map((df) => df.fieldname)
			.filter((doctype) => mandatory_table_fields.includes(doctype));

		let checkboxes = [].concat(
			...multicheck_fields.map((fieldname) => {
				let field = this.dialog.get_field(fieldname);
				return field.options
					.filter((option) => option.danger)
					.map((option) => option.$checkbox.find("input").get(0));
			})
		);

		this.unselect_all();
		$(checkboxes).prop("checked", true).trigger("change");
	}
initialize_export_field_selection() {
    console.log("initialize_export_field_selection");
    frappe.call({
        method: 'tfs.tfs.doctype.export_fields.export_fields.get_defualt_export_field',
        args: {
			 doctype: this.doctype,
		},
        callback: (response) => {
            if (response.message) {
                let result = response.message;
                console.log("get_defualt_export_field:", result);
                if (result === "select_mandatory") {
                    this.select_mandatory();  // Ensure `this` is correctly bound
                } else {
                    this.dropdown(null, result);  // Ensure `this` is correctly bound and pass `result`
                }
            }
        }
    });
}



    // select_mandatory() {
	//
    //     frappe.call({
    //         method: 'tfs.tfs.doctype.export_fields.export_fields.get_exported_checked_fields',
    //         args: {
    //             doctype: this.doctype,
    //         },
    //         callback: (response) => {
    //             if (response.message) {
    //                 let result = response.message;
	//
    //                 let mandatory_table_fields = frappe.meta
    //                     .get_table_fields(this.doctype)
	// 					// .filter((df) => df.reqd)
    //                     .map((df) => df.fieldname);
    //                 mandatory_table_fields.push(this.doctype);
	//
    //                 let multicheck_fields = this.dialog.fields
    //                     .filter((df) => df.fieldtype === "MultiCheck")
    //                     .map((df) => df.fieldname)
    //                     .filter((doctype) => mandatory_table_fields.includes(doctype));
	//
    //                 let checkboxes = [].concat(
    //                     ...multicheck_fields.map((fieldname) => {
    //                         let field = this.dialog.get_field(fieldname);
	//
	//
    //                         // Map the labels from field.options
    //                         const sortedResult = field.options.map(option => option.label);
	//
    //                         // Initialize an array to store common labels and checkboxes
    //                         let commonLabelsAndCheckboxes = [];
	//
    //                         // Check for common elements and valid field options
    //                         if (field && field.options) {
    //                             result.forEach(label => {
    //                                 if (sortedResult.includes(label)) {
    //                                     let checkbox = field.options.find(option => option.label === label);
    //                                     if (checkbox && checkbox.$checkbox) {
    //                                         commonLabelsAndCheckboxes.push({
    //                                             label: label,
    //                                             checkbox: checkbox.$checkbox.find("input").get(0)
    //                                         });
    //                                     }
    //                                 }
    //                             });
	//
    //                             // Check child table fields
    //                             frappe.meta.get_table_fields(this.doctype).forEach(df => {
    //                                 let cdt = df.options;
    //                                 let child_fieldname = df.fieldname;
    //                                 let child_multicheck = this.dialog.get_field(child_fieldname);
    //                                 if (child_multicheck) {
    //                                     child_multicheck.options.forEach(option => {
    //                                         if (result.includes(option.label)) {
    //                                             option.$checkbox.find("input").prop("checked", true).trigger("change");
    //                                         }
    //                                     });
    //                                 }
    //                             });
    //                         }
	//
    //                         return commonLabelsAndCheckboxes;
    //                     })
    //                 );
	//
    //                 this.unselect_all();
    //                 $(checkboxes.flat().map(entry => entry.checkbox)).prop("checked", true).trigger("change");
    //             }
    //         }
    //     });
    // }


    unselect_all() {
        let update_existing_records =
            this.dialog.get_value("exporting_for") == "Update Existing Records";
        this.dialog.$wrapper
            .find(`:checkbox${update_existing_records ? ":not([data-unit=name])" : ""}`)
            .prop("checked", false)
            .trigger("change");
    }

    update_record_count_message() {
        let export_records = this.dialog.get_value("export_records");
        let count_method = {
            all: () => frappe.db.count(this.doctype),
            by_filter: () =>
                frappe.db.count(this.doctype, {
                    filters: this.get_filters(),
                }),
            blank_template: () => Promise.resolve(0),
            "5_records": () => Promise.resolve(5),
        };

        count_method[export_records]().then((value) => {
            let message = "";
            value = parseInt(value, 10);
            if (value === 0) {
                message = __("No records will be exported");
            } else if (value === 1) {
                message = __("1 record will be exported");
            } else {
                message = __("{0} records will be exported", [value]);
            }
            this.dialog.set_df_property("export_records", "description", message);

            this.update_primary_action(value);
        });
    }

    update_primary_action(no_of_records) {
        let $primary_action = this.dialog.get_primary_btn();

        if (no_of_records != null) {
            let label = "";
            if (no_of_records === 0) {
                label = __("Export");
            } else if (no_of_records === 1) {
                label = __("Export 1 record");
            } else {
                label = __("Export {0} records", [no_of_records]);
            }
            $primary_action.html(label);
        } else {
            let parent_fields = this.dialog.get_value(this.doctype);
            $primary_action.prop("disabled", parent_fields.length === 0);
        }
    }

    get_filters() {
        return this.filter_group.get_filters().map((filter) => {
            return filter.slice(0, 4);
        });
    }

    get_multicheck_options(doctype, child_fieldname = null) {
        if (!this.column_map) {
            this.column_map = get_columns_for_picker(this.doctype);
        }

        let autoname_field = null;
        let meta = frappe.get_meta(doctype);
        if (meta.autoname && meta.autoname.startsWith("field:")) {
            let fieldname = meta.autoname.slice("field:".length);
            autoname_field = frappe.meta.get_field(doctype, fieldname);
        }

        let fields = child_fieldname ? this.column_map[child_fieldname] : this.column_map[doctype];

        let is_field_mandatory = (df) => {
            if (df.reqd && this.exporting_for == "Insert New Records") {
                return true;
            }
            if (autoname_field && df.fieldname == autoname_field.fieldname) {
                return true;
            }
            if (df.fieldname === "name") {
                return true;
            }
            return false;
        };

        return fields
            .filter((df) => {
                if (autoname_field && df.fieldname === "name") {
                    return false;
                }
                return true;
            })
            .map((df) => {
                return {
                    label: __(df.label),
                    value: df.fieldname,
                    danger: is_field_mandatory(df),
                    checked: false,
                    description: `${df.fieldname} ${df.reqd ? __("(Mandatory)") : ""}`,
                };
            });
    }
};

export function get_columns_for_picker(doctype) {
    let out = {};

    const exportable_fields = (df) => {
        let keep = true;
        if (frappe.model.no_value_type.includes(df.fieldtype)) {
            keep = false;
        }
        if (["lft", "rgt"].includes(df.fieldname)) {
            keep = false;
        }
        if (df.is_virtual) {
            keep = false;
        }
        return keep;
    };

    // parent
    let doctype_fields = frappe.meta.get_docfields(doctype).filter(exportable_fields);

    out[doctype] = [
        {
            label: __("ID"),
            fieldname: "name",
            fieldtype: "Data",
            reqd: 1,
        },
    ].concat(doctype_fields);

    // children
    const table_fields = frappe.meta.get_table_fields(doctype);
    table_fields.forEach((df) => {
        const cdt = df.options;
        const child_table_fields = frappe.meta.get_docfields(cdt).filter(exportable_fields);

        out[df.fieldname] = [
            {
                label: __("ID"),
                fieldname: "name",
                fieldtype: "Data",
                reqd: 1,
            },
        ].concat(child_table_fields);
    });

    return out;
}



