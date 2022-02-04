# Copyright (c) 2021, jan and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document

class Discount(Document):
    @frappe.whitelist()
    def fetch_item_groups(self, opportunity,item_groups):
        if not opportunity:
            frappe.throw("Please select Opportunity")

        data = item_groups

        query = """ SELECT BBRM.item_group FROM `tabBudget BOM` BB 
                    INNER JOIN `tabBudget BOM Raw Material` BBRM ON BBRM.parent = BB.name 
                    WHERE BB.opportunity = '{0}' and BB.docstatus=1
                """.format(opportunity)

        budget_bom = frappe.db.sql(query,as_dict=1)
        if len(budget_bom) == 0:
            frappe.throw("No Item Groups Fetched")
        item_groups_final = []
        for i in budget_bom:
            if not self.check_item_group(i, data,item_groups_final):
                item_groups_final.append(i.item_group)
        return item_groups_final

    def check_item_group(self, budget_bom, data,item_groups_final):
        for i in data:
            if budget_bom.item_group == i['item_group']:
                return True
        return budget_bom.item_group in item_groups_final

    def on_trash(self):
        bb = frappe.db.sql(""" SELECT * FROm `tabBudget BOM Raw Material` WHERE link_discount_amount=%s """, self.name,
                           as_dict=1)
        if len(bb) > 0:
            for i in bb:
                bb_status = frappe.db.sql(""" SELECT * FROm `tabBudget BOM` WHERE name=%s""", i.parent, as_dict=1)
                if bb_status[0].docstatus == 1:
                    frappe.throw("Discount is linked with Submitted Budget BOM")
        self.unlinked_discount()

    def unlinked_discount(self):
        frappe.db.sql(
            """ UPDATE `tabBudget BOM Raw Material` SET link_discount_amount=''  WHERE link_discount_amount=%s""",
            (self.name))
        frappe.db.commit()

@frappe.whitelist()
def update_budget_boms(opportunity,item_groups):
    data = json.loads(item_groups)
    for i in data:
        update_budget_bom(i,opportunity)

@frappe.whitelist()
def update_budget_bom(d, opportunity):
    try:
        discount = json.loads(d)
    except:
        discount = d

    print("DISCOUUUUUUUUNt")
    print(discount)
    if not opportunity:
        frappe.throw("Please Select Opportunity")

    if not discount['item_group']:
        frappe.throw("Please Select Valid Item Group")

    bb = frappe.db.sql(""" SELECT * FROM `tabBudget BOM` WHERE opportunity=%s """, opportunity, as_dict=1)
    for i in bb:
        bb_details = frappe.db.sql(""" SELECT * FROM `tabBudget BOM Raw Material` WHERE item_group=%s and parent=%s """, (discount['item_group'], i.name), as_dict=1)
        bb_details1 = frappe.db.sql(""" SELECT * FROM `tabBudget BOM Enclosure Raw Material` WHERE item_group=%s and parent=%s """, (discount['item_group'], i.name), as_dict=1)
        for xx in bb_details:
            discount_percentage = discount['discount_percentage']
            discount_amount = (xx.qty * xx.rate) * (discount_percentage / 100)
            amount = (xx.qty * xx.rate) - discount_amount
            discount_rate = amount / xx.qty

            frappe.db.sql(""" UPDATE `tabBudget BOM Raw Material` SET discount_percentage=%s, discount_amount=%s, amount=%s, discount_rate=%s, remarks=%s WHERE name=%s""",
                          (discount_percentage, discount_amount, amount, discount_rate,discount['remarks'] if 'remarks' in discount else "", xx.name))
            frappe.db.commit()

        for xx in bb_details1:
            discount_percentage = discount['discount_percentage']
            discount_amount = (xx.qty * xx.rate) * (discount_percentage / 100)
            amount = (xx.qty * xx.rate) - discount_amount
            discount_rate = amount / xx.qty

            frappe.db.sql(
                """ UPDATE `tabBudget BOM Enclosure Raw Material` SET discount_percentage=%s, discount_amount=%s, amount=%s, discount_rate=%s, remarks=%s WHERE name=%s""",
                (discount_percentage, discount_amount, amount, discount_rate, discount['remarks'] if 'remarks' in discount else "", xx.name))
            frappe.db.commit()

        compute_bb = frappe.db.sql(""" SELECT * FROM `tabBudget BOM Raw Material` WHERE parent=%s""", i.name, as_dict=1)
        compute_bb1 = frappe.db.sql(""" SELECT * FROM `tabBudget BOM Enclosure Raw Material` WHERE parent=%s""", i.name, as_dict=1)
        total_amount = 0
        for x in compute_bb:
            total_amount += x.amount
        for x in compute_bb1:
            total_amount += x.amount

        frappe.db.sql(
            """ UPDATE `tabBudget BOM` SET total_raw_material_cost=%s WHERE name=%s""",
            (total_amount, i.name))

        frappe.db.commit()