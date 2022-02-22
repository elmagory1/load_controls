frappe.listview_settings['Product Change Request'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["Pending"].includes(doc.status)) {
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (["Rejected"].includes(doc.status)) {
			return [__(doc.status), "red", "status,=," + doc.status];
		} else if (["Approved"].includes(doc.status)) {
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};