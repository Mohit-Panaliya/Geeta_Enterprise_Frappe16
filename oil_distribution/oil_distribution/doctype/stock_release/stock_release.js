frappe.ui.form.on('Stock Release', {
	setup(frm) {
		frm.set_query('item', 'items', function() {
			return {
				filters: { has_variants: 0 }
			};
		});
	},

	company(frm) {
		if (!frm.doc.company) return;
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Company',
				filters: { name: frm.doc.company },
				fieldname: ['abbr']
			},
			callback(r) {
				if (!r.message) return;
				const abbr = r.message.abbr;
				frm.doc.items.forEach((row) => {
					const child = frappe.get_doc('Stock Release Item', row.name);
					frappe.model.set_value(child.doctype, child.name, 'reserved_warehouse', `Reserved WH - ${abbr}`);
					frappe.model.set_value(child.doctype, child.name, 'unreserved_warehouse', `Unreserved WH - ${abbr}`);
					if (child.item) {
						fetch_qty_for_row(frm, child.doctype, child.name, abbr);
					}
				});
				frm.trigger('fetch_swastik_breakdown');
				frm.trigger('fetch_release_breakdown');
			}
		});
	},

	refresh(frm) {
		frm.trigger('fetch_swastik_breakdown');
		frm.trigger('fetch_release_breakdown');
		if (frm.doc.docstatus === 1 && frm.doc.status === 'Released') {
			frm.add_custom_button(__('View Stock Entries'), function() {
				const entries = frm.doc.items.map(i => i.stock_entry).filter(Boolean);
				if (entries.length) {
					frappe.set_route('List', 'Stock Entry', { name: ['in', entries] });
				}
			});
		}
	},

	items_add(frm) {
		frm.trigger('fetch_swastik_breakdown');
		frm.trigger('fetch_release_breakdown');
	},

	items_remove(frm) {
		frm.trigger('fetch_swastik_breakdown');
		frm.trigger('fetch_release_breakdown');
	},

	fetch_swastik_breakdown(frm) {
		const items = (frm.doc.items || []).map(r => r.item).filter(Boolean);
		if (!items.length) {
			frm.fields_dict.swastik_breakdown_html.$wrapper.html(
				'<p style="color: #888; padding: 8px;">Add items to see Swastik reserved breakdown.</p>'
			);
			return;
		}
		frm.call('get_swastik_breakdown', {
			items: items
		}).then(r => {
			if (!r || !r.message) return;
			const data = r.message;
			const companies = Object.keys(data[0]).filter(k => k !== 'item' && k !== 'item_name' && k !== 'total');
			let html = `<table class="table table-bordered" style="font-size: 13px;">
				<thead><tr><th>Item</th>`;
			companies.forEach(c => { html += `<th class="text-right">${c}</th>`; });
			html += `<th class="text-right">Total</th></tr></thead><tbody>`;
			data.forEach(row => {
				html += `<tr><td>${row.item_name || row.item}</td>`;
				companies.forEach(c => {
					html += `<td class="text-right">${Math.round(row[c])}</td>`;
				});
				html += `<td class="text-right"><b>${Math.round(row.total)}</b></td></tr>`;
			});
			html += '</tbody></table>';
			frm.fields_dict.swastik_breakdown_html.$wrapper.html(html);
		});
	},

	fetch_release_breakdown(frm) {
		const items = (frm.doc.items || []).map(r => r.item).filter(Boolean);
		if (!items.length) {
			frm.fields_dict.release_breakdown_html.$wrapper.html(
				'<p style="color: #888; padding: 8px;">Add items to see Unreserved stock breakdown.</p>'
			);
			return;
		}
		frm.call('get_release_breakdown', {
			items: items
		}).then(r => {
			if (!r || !r.message) return;
			const data = r.message;
			const companies = Object.keys(data[0]).filter(k => k !== 'item' && k !== 'item_name' && k !== 'total');
			let html = `<table class="table table-bordered" style="font-size: 13px;">
				<thead><tr><th>Item</th>`;
			companies.forEach(c => { html += `<th class="text-right">${c}</th>`; });
			html += `<th class="text-right">Total</th></tr></thead><tbody>`;
			data.forEach(row => {
				html += `<tr><td>${row.item_name || row.item}</td>`;
				companies.forEach(c => {
					html += `<td class="text-right">${Math.round(row[c])}</td>`;
				});
				html += `<td class="text-right"><b>${Math.round(row.total)}</b></td></tr>`;
			});
			html += '</tbody></table>';
			frm.fields_dict.release_breakdown_html.$wrapper.html(html);
		});
	}
});

frappe.ui.form.on('Stock Release Item', {
	item(frm, cdt, cdn) {
		const row = frappe.get_doc(cdt, cdn);
		if (!row.item || !frm.doc.company) return;

		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Item',
				filters: { name: row.item },
				fieldname: ['stock_uom']
			},
			callback(r) {
				if (r.message) {
					frappe.model.set_value(cdt, cdn, 'stock_uom', r.message.stock_uom);
				}
			}
		});

		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Company',
				filters: { name: frm.doc.company },
				fieldname: ['abbr']
			},
			callback(r) {
				if (!r.message) return;
				const abbr = r.message.abbr;
				frappe.model.set_value(cdt, cdn, 'reserved_warehouse', `Reserved WH - ${abbr}`);
				frappe.model.set_value(cdt, cdn, 'unreserved_warehouse', `Unreserved WH - ${abbr}`);
				fetch_qty_for_row(frm, cdt, cdn, abbr);
				frm.trigger('fetch_swastik_breakdown');
				frm.trigger('fetch_release_breakdown');
			}
		});
	}
});

function fetch_qty_for_row(frm, cdt, cdn, abbr) {
	const row = frappe.get_doc(cdt, cdn);
	if (!row.item) return;
	const reserved_wh = `Reserved WH - ${abbr}`;
	const unreserved_wh = `Unreserved WH - ${abbr}`;
	frappe.db.get_value('Bin', { item_code: row.item, warehouse: reserved_wh }, 'actual_qty')
		.then(r => {
			const reserved_qty = (r && r.message) ? r.message.actual_qty || 0 : 0;
			frappe.db.get_value('Bin', { item_code: row.item, warehouse: unreserved_wh }, 'actual_qty')
				.then(r2 => {
					const released_qty = (r2 && r2.message) ? r2.message.actual_qty || 0 : 0;
					frappe.model.set_value(cdt, cdn, 'reserved_qty', reserved_qty);
					frappe.model.set_value(cdt, cdn, 'already_released_qty', released_qty);
					frappe.model.set_value(cdt, cdn, 'qty', reserved_qty);
				});
		});
}
