frappe.listview_settings['Budget BOM'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["To Quotation","Approved and To Sales Order",
				"To Sales Order", "Declined and To Sales Order",
				"Waiting for Review","To Material Request and To Work Order",
				"Waiting for Accept / Decline", "To Work Order","To Revised Quotation",
				"To Supplier Quotation", "To Purchase Order","To Purchase Receipt","To Purchase Invoice", "To Deliver"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (["Rejected"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "red", "status,=," + doc.status];
		} else if ([
			"To Design", "Completed",
				"Approved", "Updated Changes",
				"Decline","To PO and SO",
			].includes(doc.status)) {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		} else if (["Quotation In Progress", "To SO", "To PO", "To Material Request","To DN and PO","To DN and PR","To SI and PR",
				"To DN and PI","To SI and PI", "To SI", "To PI"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "blue", "status,=," + doc.status];
		}

	},
};