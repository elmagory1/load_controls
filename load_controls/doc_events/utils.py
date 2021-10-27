import frappe


def check_items(doc):
    for i in doc.items:
        if i.rate > i.budget_bom_rate:
            return True

    return False

def on_submit_record(doc, method):
    if doc.doctype == "Purchase Order":
        if check_items(doc) and not doc.approve_po_rate:
            frappe.throw("PO Rate not Approved")

    for i in doc.budget_bom_reference:
        si = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabSales Invoice` SI INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = SI.name WHERE BBR.budget_bom=%s and  SI.docstatus=1""",
            i.budget_bom, as_dict=1)
        pi = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabPurchase Invoice` PI INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = PI.name WHERE BBR.budget_bom=%s and  PI.docstatus=1""",
            i.budget_bom, as_dict=1)
        dn = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabDelivery Note` DN INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = DN.name WHERE BBR.budget_bom=%s and DN.docstatus=1""",
            i.budget_bom, as_dict=1)
        pr = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabPurchase Receipt` PR INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = PR.name WHERE BBR.budget_bom=%s and  PR.docstatus=1""",
            i.budget_bom, as_dict=1)

        po = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabPurchase Order` PO INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = PO.name WHERE BBR.budget_bom=%s and  PO.docstatus=1""",
            i.budget_bom, as_dict=1)

        so = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabSales Order` SO INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = SO.name WHERE BBR.budget_bom=%s and  SO.docstatus=1""",
            i.budget_bom, as_dict=1)

        status = ""
        if doc.doctype == "Purchase Order":
            po[0].count = 1

        elif doc.doctype == "Purchase Receipt":
            pr[0].count = 1

        elif doc.doctype == "Purchase Invoice":
            pi[0].count = 1

        elif doc.doctype == "Delivery Note":
            dn[0].count = 1

        elif doc.doctype == "Sales Invoice":
            si[0].count = 1

        # Statuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuus

        if po[0].count == 0 and so[0].count > 0 and si[0].count > 0 and pi[0].count == 0 and dn[0].count == 0 and pr[0].count == 0:
            status = "To DN and PO"

        elif po[0].count == 0 and so[0].count > 0 and si[0].count > 0 and pi[0].count == 0 and dn[0].count == 0 and pr[0].count == 0:
            status = "To Material Request"

        elif po[0].count > 0 and si[0].count > 0 and pi[0].count > 0 and dn[0].count > 0 and pr[0].count > 0:
            status = "Completed"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count == 0 and dn[0].count == 0 and pr[0].count == 0:
            status = "To DN and PR"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count == 0 and dn[0].count > 0 and pr[0].count == 0:
            status = "To SI and PR"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count == 0 and dn[0].count == 0 and pr[0].count > 0:
            status = "To DN and PI"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count == 0 and dn[0].count > 0 and pr[0].count > 0:
            status = "To SI and PI"

        elif po[0].count > 0 and si[0].count > 0 and pi[0].count == 0 and dn[0].count > 0 and pr[0].count > 0:
            status = "To PI"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count > 0 and dn[0].count > 0 and pr[0].count > 0:
            status = "To SI"

        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s""", (status, i.budget_bom))
        frappe.db.commit()


def on_cancel_record(doc, method):
    for i in doc.budget_bom_reference:
        si = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabSales Invoice` SI INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = SI.name WHERE BBR.budget_bom=%s and  SI.docstatus=1""",
            i.budget_bom, as_dict=1)
        pi = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabPurchase Invoice` PI INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = PI.name WHERE BBR.budget_bom=%s and  PI.docstatus=1""",
            i.budget_bom, as_dict=1)
        dn = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabDelivery Note` DN INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = DN.name WHERE BBR.budget_bom=%s and DN.docstatus=1""",
            i.budget_bom, as_dict=1)
        pr = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabPurchase Receipt` PR INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = PR.name WHERE BBR.budget_bom=%s and  PR.docstatus=1""",
            i.budget_bom, as_dict=1)

        po = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabPurchase Order` PO INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = PO.name WHERE BBR.budget_bom=%s and  PO.docstatus=1""",
            i.budget_bom, as_dict=1)

        so = frappe.db.sql(
            """ SELECT COUNT(*) as count FROM `tabSales Order` SO INNER JOIN `tabBudget BOM References` BBR ON BBR.parent = SO.name WHERE BBR.budget_bom=%s and  SO.docstatus=1""",
            i.budget_bom, as_dict=1)

        status = ""

        if po[0].count == 0 and so[0].count > 0 and si[0].count > 0 and pi[0].count == 0 and dn[0].count == 0 and pr[0].count == 0:
            status = "To DN and PO"

        elif po[0].count == 0 and so[0].count > 0 and si[0].count > 0 and pi[0].count == 0 and dn[0].count == 0 and pr[0].count == 0:
            status = "To Material Request"

        elif po[0].count > 0 and si[0].count > 0 and pi[0].count > 0 and dn[0].count > 0 and pr[0].count > 0:
            status = "Completed"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count == 0 and dn[0].count == 0 and pr[0].count == 0:
            status = "To DN and PR"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count == 0 and dn[0].count > 0 and pr[0].count == 0:
            status = "To SI and PR"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count == 0 and dn[0].count == 0 and pr[0].count > 0:
            status = "To DN and PI"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count == 0 and dn[0].count > 0 and pr[0].count > 0:
            status = "To SI and PI"

        elif po[0].count > 0 and si[0].count > 0 and pi[0].count == 0 and dn[0].count > 0 and pr[0].count > 0:
            status = "To PI"

        elif po[0].count > 0 and si[0].count == 0 and pi[0].count > 0 and dn[0].count > 0 and pr[0].count > 0:
            status = "To SI"

        frappe.db.sql(""" UPDATE `tabBudget BOM` SET status=%s WHERE name=%s""", (status, i.budget_bom))
        frappe.db.commit()



