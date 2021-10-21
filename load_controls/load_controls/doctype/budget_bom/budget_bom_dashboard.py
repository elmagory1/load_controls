from frappe import _


def get_data():
	return {
		'fieldname': 'budget_bom',
		'non_standard_fieldnames': {
			'Quotation': 'budget_bom',
			'Sales Order': 'budget_bom',
			'Material Request': 'budget_bom',
			'Purchase Order': 'budget_bom',
			'Purchase Invoice': 'budget_bom',
			'Purchase Receipt': 'budget_bom',
		},
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': [
					"Quotation", "BOM", "Sales Order",
					"Material Request", "Purchase Order",
					"Purchase Invoice", "Purchase Receipt"]
			}
		]
	}