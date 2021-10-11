# Copyright (c) 2021, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BudgetBOM(Document):
	@frappe.whitelist()
	def generate_quotation(self):
		obj = {
			"doctype": "Quotation",
			"quotation_to": "Customer",
			"transaction_date": self.posting_date,
			"valid_till": self.posting_date,
			"party_name": self.customer,
			"budget_bom": self.name,
			"items": [{
				"item_code": self.fg_sellable_bom_details[0].item_code,
				"item_name": self.fg_sellable_bom_details[0].item_name,
				"qty": self.fg_sellable_bom_details[0].qty,
				"uom": self.fg_sellable_bom_details[0].uom,
			}]
		}
		print("QUOTATION")
		print(obj)
		quotation = frappe.get_doc(obj).insert()
		frappe.db.sql(""" UPDATE `tabBudget BOM` SET status='To Quotation', quotation_amended=0 WHERE name=%s """,
					  self.name)
		frappe.db.commit()
		return quotation.name

	@frappe.whitelist()
	def get_quotation(self):
		quotation = frappe.db.sql(""" SELECT COUNT(*) as count, docstatus FROM `tabQuotation` WHERE budget_bom=%s and docstatus < 2""", self.name, as_dict=1)

		return quotation[0].count > 0


	@frappe.whitelist()
	def amend_quotation(self):
		quotation = frappe.db.sql(""" SELECT * FROM `tabQuotation` WHERE budget_bom=%s and docstatus=1""", self.name, as_dict=1)
		q = frappe.get_doc("Quotation", quotation[0].name)
		q.cancel()
		frappe.db.sql(""" UPDATE `tabBudget BOM` SET status='To Quotation', quotation_amended=1 WHERE name=%s """, self.name)
		frappe.db.commit()

	@frappe.whitelist()
	def action_to_design(self, status):
		updated_status = "To Purchase Order" if status == "Approve" else "Pending" if status == "Update" else "Rejected"
		if status == "Approve":
			frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s, quotation_amended=%s WHERE name=%s """,
						  (updated_status,updated_status == "Pending",self.name))
			frappe.db.commit()