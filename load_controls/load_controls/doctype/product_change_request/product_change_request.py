# Copyright (c) 2022, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProductChangeRequest(Document):
	@frappe.whitelist()
	def get_mr_items(self):
		items = []
		for i in self.addition:
			items.append({
				"t_warehouse": i.target_warehouse,
				"item_code": i.item,
				"qty": i.qty,
				"uom": i.uom,
				"conversion_factor": 1,
				"schedule_date": self.required_by,
				"rate": i.rate,
			})
		return items
	@frappe.whitelist()
	def generate_mr(self):
		obj = {
			"doctype": "Material Request",
			"purpose": "Purchase",
			"schedule_date": self.required_by,
			"items": self.get_mr_items(),
			"budget_bom_reference": [{"budget_bom":self.budget_bom}]
		}
		se = frappe.get_doc(obj).insert()
		se.submit()
		frappe.db.sql(""" UPDATE `tabProduct Change Request` SET material_request=%s WHERE name=%s""", (se.name, self.name))
		frappe.db.commit()

	@frappe.whitelist()
	def generate_se(self):
		obj = {
			"doctype": "Stock Entry",
			"stock_entry_type": "Manufacture",
			"items": self.get_items()
		}
		se = frappe.get_doc(obj).insert()
		se.submit()
		frappe.db.sql(""" UPDATE `tabProduct Change Request` SET stock_entry=%s WHERE name=%s""", (se.name, self.name))
		frappe.db.commit()
	@frappe.whitelist()
	def get_items(self):
		items = []
		for i in self.addition:
			items.append({
				"t_warehouse": i.target_warehouse,
				"item_code": i.item,
				"qty": i.qty,
				"uom": i.uom,
				"conversion_factor": 1,
				"basic_rate": i.rate,
			})
		for i in self.deletion:
			items.append({
				"s_warehouse": i.source_warehouse,
				"item_code": i.item,
				"qty": i.qty,
				"uom": i.uom,
				"conversion_factor": 1,
				"basic_rate": i.rate,
			})
		return items

	@frappe.whitelist()
	def get_budget_bom(self):
		bb = frappe.get_doc("Budget BOM", self.budget_bom)
		addition_fields = ["electrical_bom_additiondeletion","mechanical_bom_additiondeletion"]
		incoming_total = 0
		outgoing_total = 0
		for x in addition_fields:
			for i in bb.__dict__[x]:
				if i.type == "Addition":
					self.append("addition", {
						"item": i.item_code,
						"item_name": i.item_name,
						"qty": i.qty,
						"uom": i.uom,
						"rate": i.rate,
						"amount": i.amount,
						"available_qty": i.available_qty,
					})
					incoming_total += i.amount
				if i.type == "Deletion":
					self.append("deletion", {
						"item": i.item_code,
						"item_name": i.item_name,
						"qty": i.qty,
						"uom": i.uom,
						"rate": i.rate,
						"amount": i.amount,
						"available_qty": i.available_qty,
					})
					outgoing_total += i.amount

		return incoming_total, outgoing_total


	@frappe.whitelist()
	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabProduct Change Request` SET status=%s WHERE name=%s""", (status, self.name))
		frappe.db.commit()
