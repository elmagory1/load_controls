# Copyright (c) 2021, jan and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.stock_ledger import get_previous_sle

class BudgetBOM(Document):
    @frappe.whitelist()
    def request_for_revise(self):
        frappe.db.sql(""" UPDATE `tabBudget BOM` SET request=1 WHERE name=%s """, self.name)
        frappe.db.commit()
    @frappe.whitelist()
    def submit_for_approval(self):
        frappe.db.sql(""" UPDATE `tabBudget BOM` SET submitted_changes=1, status=%s WHERE name=%s """, ("Waiting for Review", self.name))
        frappe.db.commit()

    def on_cancel(self):

        frappe.db.sql(""" UPDATE `tabOpportunity` SET budget_bom='' WHERE name=%s """, self.opportunity)
        frappe.db.commit()

    def on_update_after_submit(self):
        allow_tmr = frappe.db.get_single_value('Manufacturing Settings', 'allow_budget_bom_total_raw_material_cost')
        if self.status == 'To Design':
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET updated_changes=%s WHERE name=%s """,(self.additiondeletion_raw_material_subtotal >= allow_tmr,self.name))
            frappe.db.commit()
            self.reload()

    @frappe.whitelist()
    def update_discounts(self):
        fields = ['electrical_bom_raw_material', 'mechanical_bom_raw_material', 'fg_sellable_bom_raw_material']
        for i in fields:
            for ii in self.__dict__[i]:
                obj = self.update_discount(ii.__dict__)

    @frappe.whitelist()
    def update_discount(self, item):
        discount = frappe.db.sql(""" SELECT * FROm `tabDiscount` WHERE opportunity=%s and item_code=%s and item_group=%s """,
                                 (self.opportunity, item['item_code'], item['item_group']), as_dict=1)

        if len(discount) > 0:
            item['discount_rate'] = discount[0].discount_rate
            item['link_discount_amount'] = discount[0].name
            item['discount_amount'] = discount[0].discount_amount
            item['discount_percentage'] = discount[0].discount_percentage
            item['rate'] = (discount[0].discount_rate * item['qty']) + discount[0].discount_amount
            item['amount'] = (discount[0].discount_rate * item['qty'])

    @frappe.whitelist()
    def get_templates(self, templates, raw_material_table):
        raw_material_warehouse = frappe.db.get_single_value('Manufacturing Settings', 'default_raw_material_warehouse')
        for i in templates:
            template = frappe.get_doc("BOM Item Template", i)

            for x in template.items:
                item_master = frappe.get_doc("Item", x.item_code)
                rate = get_rate(x.item_code, "",self.rate_of_materials_based_on if self.rate_of_materials_based_on else "", self.price_list if self.price_list else "")
                obj = {
                    'item_code': x.item_code,
                    'item_name': item_master.item_name,
                    'uom': x.uom,
                    'qty': x.qty,
                    'warehouse': raw_material_warehouse,
                    'rate': rate[0],
                    'amount': rate[0] * x.qty,
                    'discount_rate': 0
                }
                discount = frappe.db.sql(""" 
                                                      SELECT D.name, DD.item_group, DD.discount_percentage, DD.remarks FROM `tabDiscount` D INNER JOIN `tabDiscount Details` DD ON DD.parent = D.name WHERE D.opportunity=%s and DD.item_group=%s """,
                                         (self.opportunity, item_master.item_group), as_dict=1)
                if len(discount) > 0:
                    obj['discount_percentage'] = discount[0].discount_percentage
                    obj['discount_amount'] = (discount[0].discount_percentage / 100) * rate[0] * x.qty
                    obj['amount'] = (rate[0] * (x.conversion_factor * x.qty)) - obj['discount_amount']
                    obj['discount_rate'] = obj['amount'] / x.qty
                    obj['remarks'] = discount[0].remarks
                    obj['link_discount_amount'] = discount[0].name
                    obj['rate'] = (obj['discount_rate'] * x.qty) + obj['discount_amount']

                self.append(raw_material_table,obj)

    @frappe.whitelist()
    def add_or_save_discount(self, opportunity, item_group, discount_percentage, remarks):
        disc = frappe.db.sql(""" SELECT COUNT(*) as count, name FROM `tabDiscount` WHERE opportunity=%s """,
                             opportunity, as_dict=1)
        if disc[0].count > 0:
            discount = frappe.get_doc("Discount", disc[0].name)
            discount.append("discount_details", {
                "item_group": item_group,
                "discount_percentage": discount_percentage
            })
            discount.save()
            return disc[0].name
        else:
            obj = {
                "doctype": "Discount",
                "opportunity": opportunity,
                "discount_details": [{
                    "item_group": item_group,
                    "discount_percentage": discount_percentage,
                    "remarks": remarks
                }]
            }
            d = frappe.get_doc(obj).insert()
            return d.name

    @frappe.whitelist()
    def get_discount(self, item,raw_material_table):
        raw_material_warehouse = frappe.db.get_single_value('Manufacturing Settings', 'default_raw_material_warehouse')
        item_master = frappe.get_doc("Item", item['item_code'])

        rate = get_rate(item['item_code'], "", self.rate_of_materials_based_on if self.rate_of_materials_based_on else "",
                        self.price_list if self.price_list else "")
        obj = {
            'item_code': item['item_code'],
            'item_name': item_master.item_name,
            'item_group': item_master.item_group,
            'uom': item['uom'],
            'qty': item['qty'],
            'warehouse': raw_material_warehouse,
            'rate': rate[0],
            'amount': rate[0] * item['qty'],
            'discount_rate': 0

        }
        discount = frappe.db.sql(""" 
                                           SELECT D.name, DD.item_group, DD.discount_percentage, DD.remarks FROM `tabDiscount` D INNER JOIN `tabDiscount Details` DD ON DD.parent = D.name WHERE D.opportunity=%s and DD.item_group=%s """,
                                 (self.opportunity, item_master.item_group), as_dict=1)

        if len(discount) > 0:
            obj['discount_percentage'] = discount[0].discount_percentage
            obj['discount_amount'] = (discount[0].discount_percentage / 100) * rate[0] * item['qty']
            obj['amount'] = (rate[0] * item['qty']) - obj['discount_amount']
            obj['discount_rate'] = obj['amount'] / item['qty']
            obj['remarks'] = discount[0].remarks
            obj['link_discount_amount'] = discount[0].name
            obj['rate'] = (obj['discount_rate'] * item['qty']) + obj['discount_amount']

        return obj
    @frappe.whitelist()
    def on_submit(self):
        if self.opportunity:
            frappe.db.sql(""" UPDATE `tabOpportunity` SET budget_bom=%s WHERE name=%s""", (self.name, self.opportunity))
            frappe.db.commit()

    @frappe.whitelist()
    def generate_quotation(self):
        obj = {
            "doctype": "Quotation",
            "quotation_to": "Customer",
            "transaction_date": self.posting_date,
            "valid_till": self.posting_date,
            "party_name": self.customer,
            "additional_operating_cost": self.total_additional_operation_cost,
            "budget_bom_reference": [{
                "budget_bom": self.name
            }],
            "budget_bom_opportunity": [{
                "opportunity": self.opportunity
            }],
            "items": [{
                "item_code": self.fg_sellable_bom_details[0].item_code,
                "item_name": self.fg_sellable_bom_details[0].item_name,
                "qty": self.fg_sellable_bom_details[0].qty,
                "uom": self.fg_sellable_bom_details[0].uom,
                "rate": self.total_cost,
            }]
        }
        quotation = frappe.get_doc(obj).insert()
        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status='To Quotation', quotation_amended=0 WHERE name=%s """,
                      self.name)
        frappe.db.commit()
        return quotation.name

    @frappe.whitelist()
    def get_quotation(self):
        quotation = frappe.db.sql(""" 
                          SELECT COUNT(*) as count, Q.docstatus
                           FROM tabQuotation as Q
                           INNER JOIN `tabBudget BOM References` as BBR ON BBR.parent = Q.name
                          WHERE BBR.budget_bom=%s and Q.docstatus < 2""", self.name, as_dict=1)

        return quotation[0].count > 0

    @frappe.whitelist()
    def check_sales_order(self):
        quotation = frappe.db.sql(""" 
                          SELECT COUNT(*) as count, SO.docstatus, SO.status
                           FROM `tabSales Order`as SO
                           INNER JOIN `tabBudget BOM References` as BBR ON BBR.parent = SO.name
                          WHERE BBR.budget_bom=%s and SO.docstatus < 2 and SO.status in ('To Deliver and Bill', 'Overdue')""", self.name, as_dict=1)

        return quotation[0].count > 0

    @frappe.whitelist()
    def amend_quotation(self):
        quotation = frappe.db.sql(""" SELECT * FROM `tabQuotation` Q INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = Q.name WHERE BBR.budget_bom=%s and Q.docstatus=1""", self.name, as_dict=1)
        q = frappe.get_doc("Quotation", quotation[0].name)
        q.cancel()
        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status='To Quotation' WHERE name=%s """, self.name)
        frappe.db.commit()

    @frappe.whitelist()
    def action_to_design(self, status):
        if status == "To Material Request":
            frappe.db.sql(""" UPDATE `tabBudget BOM` SET submitted_changes=1 WHERE name=%s """, self.name)
            frappe.db.commit()
            if self.old_data:
                old_data_fetch = json.loads(self.old_data)
                fields = [
                    "posting_date",
                    "expected_closing_date",
                    "rate_of_materials_based_on",
                    "price_list",
                    "total_operation_cost",
                    "total_additional_operation_cost",
                    "discount_percentage",
                    "discount_amount",
                    "margin_",
                    "total_cost",
                    "quotation_amended",
                    "quotation_cancelled",
                ]
                obj = {}
                for i in fields:
                    obj[i] = old_data_fetch[i]
                frappe.db.set_value(self.doctype, self.name, obj)

                frappe.db.set_value("Budget BOM Raw Material", self.name, obj)

                tables = ['electrical_bom_details','mechanical_bom_details','fg_sellable_bom_details','electrical_bom_raw_material','mechanical_bom_raw_material','fg_sellable_bom_raw_material', "additional_operation_cost"]
                for table in tables:
                    for row in old_data_fetch[table]:
                        doctype = row['doctype']
                        del row['doctype']
                        frappe.db.set_value(doctype, row['name'], row)

        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s, quotation_amended=%s WHERE name=%s """,
                      (status,status == "Updated Changes",self.name))
        frappe.db.commit()

    @frappe.whitelist()
    def check_bom(self):
        bom = frappe.db.sql(""" 
                            SELECT COUNT(*) as count
                             FROM tabBOM
                            WHERE budget_bom=%s and docstatus < 2""", self.name, as_dict=1)

        return bom[0].count > 0
    @frappe.whitelist()
    def create_bom(self):
        self.create_first_bom()


    @frappe.whitelist()
    def create_first_bom(self):
        for i in self.electrical_bom_details:
            obj = {
                "doctype": "BOM",
                "item": i.item_code,
                "budget_bom":self.name,
                "with_operations":1,
                "quantity": i.qty,
                "rm_cost_as_per": self.rate_of_materials_based_on,
                "items": self.get_raw_materials("electrical_bom_raw_material"),
                "operations": self.get_operations("electrical_bom_details")
            }
            print("OBJEEEEEEEEEECT")
            print(obj)
            bom = frappe.get_doc(obj).insert()
            bom.submit()
            self.first_bom = bom.name

            self.create_second_bom()
    @frappe.whitelist()
    def create_second_bom(self):
        for i in self.mechanical_bom_details:
            obj = {
                "doctype": "BOM",
                "item": i.item_code,
                "budget_bom": self.name,
                "quantity": i.qty,
                "with_operations": 1,
                "rm_cost_as_per": self.rate_of_materials_based_on,
                "items": self.get_raw_materials("mechanical_bom_raw_material"),
                "operations": self.get_operations("mechanical_bom_details")
            }
            bom = frappe.get_doc(obj).insert()
            bom.submit()

            self.second_bom = bom.name
            self.create_third_bom()

    @frappe.whitelist()
    def create_third_bom(self):
        for i in self.fg_sellable_bom_details:
            obj = {
                "doctype": "BOM",
                "item": i.item_code,
                "quantity": i.qty,
                "with_operations": 1,
                "budget_bom": self.name,
                "rm_cost_as_per": self.rate_of_materials_based_on,
                "items": self.get_raw_materials("mechanical_bom_details", "Third") + self.get_raw_materials("electrical_bom_details", "Third") + self.get_raw_materials("fg_sellable_bom_raw_material"),
                "operations": self.get_operations("fg_sellable_bom_details")
            }

            bom = frappe.get_doc(obj).insert()
            bom.submit()

    @frappe.whitelist()
    def get_operations(self,raw_material):

        operations = []
        for i in self.__dict__[raw_material]:
            operation_record= frappe.db.sql(""" SELECT * FROM `tabWorkstation` WHERE name=%s""", i.workstation, as_dict=1)
            operation_time = operation_record[0].operation_time if len(operation_record) > 0 else 0

            operations.append({
                "operation": i.operation,
                "workstation": i.workstation,
                "time_in_mins": operation_time,
                "operating_cost": i.net_hour_rate,
            })
        return operations
    @frappe.whitelist()
    def get_raw_materials(self, raw_material, bom = None):
        items = []
        for i in self.__dict__[raw_material]:
            obj = {
                "item_code": i.item_code,
                "item_name": i.item_name,
                "rate": i.rate if 'rate' in i.__dict__ else 0,
                "qty": i.qty,
                "uom": i.uom,
                "operation_time_in_minutes": i.operation_time_in_minutes if 'operation_time_in_minutes' in i.__dict__ else 0,
                "amount": i.qty * i.rate if 'rate' in i.__dict__ else 0,
            }
            if bom == "Third" and raw_material == "mechanical_bom_details":
                obj['bom_no'] = self.second_bom

            elif bom == "Third" and raw_material == "electrical_bom_details":
                obj['bom_no'] = self.first_bom

            items.append(obj)

        print("OBJEEEEEEECT")
        print(items)
        return items

@frappe.whitelist()
def set_available_qty(items):
    data = json.loads(items)
    time = frappe.utils.now_datetime().time()
    date = frappe.utils.now_datetime().date()
    for d in data:

        previous_sle = get_previous_sle({
            "item_code": d['item_code'],
            "warehouse": d['warehouse'],
            "posting_date": date,
            "posting_time": time
        })
        d['available_qty'] = previous_sle.get("qty_after_transaction") or 0
    print(data)
    return data
def get_template_items(items):
    items_ = []
    for i in items:
        item_master = frappe.get_doc("Item", i['item_code'])
        items_.append({
            "item_code": i['item_code'],
            "item_name": item_master.item_name,
            "batch": i['batch'] if 'batch' in i and i['batch'] else "",
            "qty": i['qty'],
            "uom": i['uom'] if 'uom' in i and i['uom'] else "",
        })
    return items_
@frappe.whitelist()
def generate_item_templates(items, description):
    print("GENEEEEEEEEEEEEEEEEEEEEEEEEERAAAAAAAAAAAAAAAAAAAAAATE")
    data = json.loads(items)
    obj = {
        "doctype": "BOM Item Template",
        "description": description,
        "items": get_template_items(data)
    }

    frappe.get_doc(obj).insert()
    return data

@frappe.whitelist()
def make_mr(source_name, target_doc=None):
    # print("==================================================")
    # doc = get_mapped_doc("Budget BOM", source_name, {
    #     "Budget BOM": {
    #         "doctype": "Material Request",
    #         "validation": {
    #             "docstatus": ["=", 1]
    #         }
    #     },
    #     "Budget BOM Raw Material": {
    #         "doctype": "Material Request Item",
    #     }
    #
    # }, target_doc)
    #
    # return doc
    print(source_name)
    print(target_doc)
    doc = get_mapped_doc("Budget BOM", source_name, {
        "Budget BOM": {
            "doctype": "Material Request",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Budget BOM Raw Material": {
            "doctype": "Material Request Item",
            "field_map":{
                "name": "budget_bom_raw_material"
            }
        },
        "Budget BOM Enclosure Raw Material": {
            "doctype": "Material Request Item",
            "field_map": {
                "name": "budget_bom_raw_material"
            }
        }

    }, ignore_permissions=True)
    print("DOOOOOOOOOOOOOOOOOOOOOC")
    print(str(frappe.db.get_value("Budget BOM", source_name, "expected_closing_date")))
    doc.schedule_date = str(frappe.db.get_value("Budget BOM", source_name, "expected_closing_date"))
    for i in doc.items:
        i.schedule_date = str(frappe.db.get_value("Budget BOM", source_name, "expected_closing_date"))

    doc.append("budget_bom_reference", {
        "budget_bom": source_name
    })
    print(doc.as_dict())
    return doc


@frappe.whitelist()
def get_rate(item_code, warehouse, based_on,price_list):
    time = frappe.utils.now_datetime().time()
    date = frappe.utils.now_datetime().date()
    balance = 0
    if warehouse:
        previous_sle = get_previous_sle({
            "item_code": item_code,
            "warehouse": warehouse,
            "posting_date": date,
            "posting_time": time
        })
        # get actual stock at source warehouse
        balance = previous_sle.get("qty_after_transaction") or 0

    condition = ""
    if price_list == "Standard Buying":
        condition += " and buying = 1 "
    elif price_list == "Standard Selling":
        condition += " and selling = 1 and price_list='{0}'".format('Standard Selling')

    query = """ SELECT * FROM `tabItem Price` WHERE item_code=%s {0} ORDER BY valid_from DESC LIMIT 1""".format(condition)

    item_price = frappe.db.sql(query,item_code, as_dict=1)
    rate = item_price[0].price_list_rate if len(item_price) > 0 else 0
    print(based_on)
    if based_on == "Valuation Rate":
        item_record = frappe.db.sql(
            """ SELECT * FROM `tabItem` WHERE item_code=%s""",
            item_code, as_dict=1)
        rate = item_record[0].valuation_rate if len(item_record) > 0 else 0
    if based_on == "Last Purchase Rate":
        item_record = frappe.db.sql(
            """ SELECT * FROM `tabItem` WHERE item_code=%s""",
            item_code, as_dict=1)
        rate = item_record[0].last_purchase_rate if len(item_record) > 0 else 0

    return rate, balance

@frappe.whitelist()
def unlink(name):
    frappe.db.sql(""" UPDATE `tabBudget BOM Raw Material` SET link_discount_amount='', unlinked=1 WHERE name=%s""", name)
    frappe.db.sql(""" UPDATE `tabBudget BOM Enclosure Raw Material` SET link_discount_amount='', unlinked=1 WHERE name=%s""", name)
    frappe.db.sql(""" UPDATE `tabBudget BOM Raw Material Modifier` SET link_discount_amount='', unlinked=1 WHERE name=%s""", name)
    frappe.db.commit()