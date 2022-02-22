# Copyright (c) 2022, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ConsumableIssueNote(Document):
	@frappe.whitelist()
	def generate_se(self):
		obj = {
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"items": self.get_items()
		}
		se = frappe.get_doc(obj).insert()
		frappe.db.sql(""" UPDATE `tabConsumable Issue Note` SET stock_entry=%s WHERE name=%s""", (se.name, self.name))
		frappe.db.commit()
		se.submit()

	def get_items(self):
		difference_account = frappe.db.get_single_value('Manufacturing Settings', 'difference_account')
		if not difference_account:
			frappe.throw("Please set default Difference Account in Manufacturing Settings")
		items = []
		for i in self.items:
			items.append({
				"t_warehouse": self.warehouse,
				"item_code": i.item_code,
				"qty": i.qty,
				"cost_center": self.cost_center,
				"expense_account": difference_account
			})

		return items
