frappe.listview_settings['Budget BOM'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["To Quotation", "To Design"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (doc.status === "Completed") {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};