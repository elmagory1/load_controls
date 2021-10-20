frappe.listview_settings['Budget BOM'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["To Quotation"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (["Rejected"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "red", "status,=," + doc.status];
		} else if (["To Design", "Completed", "Approved", "Updated Changes", "Decline","To PO and SO"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		} else if (["Quotation In Progress", "To SO", "To PO", "To Material Request"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "blue", "status,=," + doc.status];
		}

	},
};