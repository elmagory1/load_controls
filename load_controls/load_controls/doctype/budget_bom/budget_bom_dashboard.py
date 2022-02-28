from frappe import _


def get_data():
	return {
		'fieldname': 'budget_bom',
		'non_standard_fieldnames': {
			'Quotation': 'budget_bom',
			'Request for Quotation': 'budget_bom',
			'Supplier Quotation': 'budget_bom',
			'Sales Order': 'budget_bom',
			'Material Request': 'budget_bom',
			'Purchase Order': 'budget_bom',
			'Purchase Invoice': 'budget_bom',
			'Purchase Receipt': 'budget_bom',
			'Gate Pass': 'budget_bom',
			'Job Card': 'budget_bom',
			'Stock Entry': 'budget_bom',
			'Work Order': 'budget_bom',
			'Delivery Note': 'budget_bom',
		},
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': [
					"Quotation", "BOM", "Sales Order","Material Request"]
			},
			{
				'label': _('Linked Forms'),
				'items': ["Purchase Order","Purchase Invoice", "Purchase Receipt","Gate Pass"]
			},
			{
				'label': _('Linked Forms'),
				'items': ["Request for Quotation", "Supplier Quotation", "Delivery Note", "Work Order"]
			},
			{
				'label': _('Linked Forms'),
				'items': ["Job Card", "Stock Entry", "Product Change Request", "Job Subcontor"]
			}
		]
	}