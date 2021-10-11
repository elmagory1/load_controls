frappe.listview_settings['Budget BOM'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["To Quotation", "To Design", "Pending", "To Purchase Order"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (["Rejected"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "red", "status,=," + doc.status];
		} else if (doc.status === "Approved") {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};