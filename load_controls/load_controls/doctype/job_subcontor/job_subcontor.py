# Copyright (c) 2022, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class JobSubcontor(Document):
	@frappe.whitelist()
	def get_budget_bom(self):
		bb = frappe.get_doc("Budget BOM", self.budget_bom)
		addition_fields = ["electrical_bom_raw_material", "mechanical_bom_raw_material", "fg_sellable_bom_raw_material"]
		for x in addition_fields:
			for i in bb.__dict__[x]:
				self.append("items", {
					"item": i.item_code,
					"item_name": i.item_name,
					"qty": i.qty,
					"uom": i.uom,
					"rate": i.rate,
					"amount": i.amount,
				})
		for i in bb.additional_operation_cost:
			self.append("additional_cost", {
				"cost_type": i.account,
				"description": i.description,
				"amount": i.amount,
			})



	@frappe.whitelist()
	def generate_po(self):
		obj = {
			"doctype": "Purchase Order",
			"supplier": self.supplier,
			"supplier_name": self.supplier_name,
			"schedule_date": self.requried_by,
			"items": self.get_po_items(),
			"budget_bom_reference": [{"budget_bom": self.budget_bom}]
		}
		po = frappe.get_doc(obj).insert()
		po.submit()
		frappe.db.sql(""" UPDATE `tabProduct Change Request` SET purchase_order=%s WHERE name=%s""",
					  (po.name, self.name))
		frappe.db.commit()
	@frappe.whitelist()
	def get_po_items(self):
		items = []
		for i in self.items:
			items.append({
				"item_code": i.item,
				"item_name": i.item_name,
				"description": i.item_name,
				"qty": i.qty,
				"uom": i.uom,
				"conversion_factor": 1,
				"schedule_date": self.required_by,
				"rate": i.rate,
			})
		return items
