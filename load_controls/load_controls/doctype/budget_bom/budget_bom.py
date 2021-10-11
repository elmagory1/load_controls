# Copyright (c) 2021, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
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

		frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s, quotation_amended=%s WHERE name=%s """,
					  (updated_status,updated_status == "Pending",self.name))
		frappe.db.commit()

	@frappe.whitelist()
	def create_bom(self):
		self.create_first_bom()
		self.create_second_bom()
		self.create_third_bom()

	@frappe.whitelist()
	def create_first_bom(self):
		for i in self.electrical_bom_details:
			obj = {
				"doctype": "BOM",
				"item": i.item_code,
				"budget_bom":self.name,
				"quantity": i.qty,
				"rm_cost_as_per": self.rate_of_materials_based_on,
				"items": self.get_raw_materials("electrical_bom_raw_material")
			}
			bom = frappe.get_doc(obj).insert()
			# bom.submit()

	@frappe.whitelist()
	def create_second_bom(self):
		for i in self.mechanical_bom_details:
			obj = {
				"doctype": "BOM",
				"item": i.item_code,
				"budget_bom": self.name,
				"quantity": i.qty,
				"rm_cost_as_per": self.rate_of_materials_based_on,
				"items": self.get_raw_materials("mechanical_bom_raw_material")
			}
			bom = frappe.get_doc(obj).insert()
			# bom.submit()

	# @frappe.whitelist()
	# def create_third_bom(self):
	# 	for i in self.fg_sellable_bom_details:
	# 		obj = {
	# 			"doctype": "BOM",
	# 			"item": i.item_code,
	# 			"quantity": i.qty,
	# 			"budget_bom": self.name,
	# 			"rm_cost_as_per": self.rate_of_materials_based_on,
	# 			"items": self.get_raw_materials("fg_sellable_bom_raw_material") + elf.get_raw_materials("fg_sellable_bom_raw_material")
	# 		}
	# 		bom = frappe.get_doc(obj).insert()
	# 		# bom.submit()

	@frappe.whitelist()
	def get_raw_materials(self, raw_material):
		items = []
		for i in self.__dict__[raw_material]:
			items.append({
				"item_code": i.item_code,
				"item_name": i.item_name,
				"rate": i.rate,
				"qty": i.qty,
				"uom": i.uom,
				"amount": i.qty * i.rate,
			})
		return items

@frappe.whitelist()
def make_mr(source_name, target_doc=None):
    print("==================================================")
    doc = get_mapped_doc("Budget BOM", source_name, {
        "Budget BOM": {
            "doctype": "Material Request",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Budget BOM Raw Material": {
            "doctype": "Material Request Item",
        }

    }, target_doc)

    return doc