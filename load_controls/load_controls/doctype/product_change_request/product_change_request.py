# Copyright (c) 2022, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from load_controls.load_controls.doctype.budget_bom.budget_bom import get_rate
class ProductChangeRequest(Document):
    @frappe.whitelist()
    def validate(self):
        if not self.project_code:
            so = frappe.db.sql(
                """  SELECT BBR.project_code FROM `tabSales Order` SO INNER JOIN `tabSales Order Item` BBR ON BBR.parent = SO.name WHERE SO.docstatus=1 and BBR.budget_bom=%s""",
                self.budget_bom, as_dict=1)
            if len(so) > 0:
                self.project_code = so[0].project_code
    @frappe.whitelist()
    def get_bb_items(self):
        print("HERE")
        items = []
        if self.work_order:
            pick_items = frappe.db.sql(""" SELECT * FROm `tabPick List` PL INNER JOIN `tabPick List Item` PLI ON PLI.parent = PL.name WHERE PL.work_order=%s""",self.work_order,as_dict=1)
            print("PICK ITEMS")
            print(pick_items)
            for i in pick_items:
                item_code = i.alternative_item if i.alternative_item else i.item_code
                items.append(item_code)
        return items
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
            other_info = get_rate(i.item, i.target_warehouse, "Last Purchase Rate","")
            items.append({
                "t_warehouse": i.target_warehouse,
                "item_code": i.item,
                "qty": i.qty,
                "uom": i.uom,
                "conversion_factor": 1,
                "basic_rate": i.rate,
                "rate":other_info[0],
                "available_qty":other_info[1],
            })
        for i in self.deletion:
            other_info = get_rate(i.item, i.target_warehouse, "Last Purchase Rate","")

            items.append({
                "s_warehouse": i.source_warehouse,
                "item_code": i.item,
                "qty": i.qty,
                "uom": i.uom,
                "conversion_factor": 1,
                "basic_rate": i.rate,
                "rate":other_info[0],
                "available_qty":other_info[1],
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
                rate = get_rate(i.item_code,"","","Standard Buying")[0]
                if i.type == "Addition":
                    self.append("addition", {
                        "item": i.item_code,
                        "item_name": i.item_name,
                        "qty": i.qty,
                        "uom": i.uom,
                        "rate": rate,
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
                        "rate": rate,
                        "amount": i.amount,
                        "available_qty": i.available_qty,
                    })
                    outgoing_total += i.amount
        so = frappe.db.sql(
                """  SELECT BBR.project_code FROM `tabSales Order` SO INNER JOIN `tabSales Order Item` BBR ON BBR.parent = SO.name WHERE SO.docstatus=1 and BBR.budget_bom=%s""",
                self.budget_bom, as_dict=1)
        so_name = ""
        cost_center_name = ""
        if len(so) > 0:
            so_name = so[0].parent
            cost_center_name = so[0].project_code
        return incoming_total, outgoing_total, so_name,cost_center_name


    @frappe.whitelist()
    def change_status(self, status):
        frappe.db.sql(""" UPDATE `tabProduct Change Request` SET status=%s WHERE name=%s""", (status, self.name))
        frappe.db.commit()
