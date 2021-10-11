from frappe import _


def get_data():
	return {
		'fieldname': 'budget_bom',
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': ["Quotation", "BOM"]
			}
		]
	}