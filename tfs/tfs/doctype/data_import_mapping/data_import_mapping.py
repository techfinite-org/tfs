# Copyright (c) 2023, Techfinite Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class DataImportMapping(Document):
	def before_save(self):
		template_json = {}
		column_to_field_map = {}
		mapping_configuration = self.mapping_columns
		for record in mapping_configuration:
			if record.column_index_in_import_file != None and record.column_index_in_import_file != "":
				column_to_field_map[record.column_index_in_import_file] = record.column_in_doctype
		template_json['column_to_field_map'] = column_to_field_map
		self.template = json.dumps(template_json)