# Copyright (c) 2022, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class JobSubcontor(Document):
	@frappe.whitelist()
	def generate_po(self):
		pass
