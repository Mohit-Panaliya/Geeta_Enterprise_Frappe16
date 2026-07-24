import json

import frappe
from frappe import _
from frappe.utils import flt, nowdate


class StockReservation(frappe.model.document.Document):
	def validate(self):
		self.set_missing_values()
		self.validate_warehouse_company()
		self.validate_warehouse_not_reserved_or_unreserved()
		self.set_reserved_and_unreserved_warehouses()

	def set_missing_values(self):
		if not self.posting_date:
			self.posting_date = nowdate()
		if not self.status:
			self.status = "Draft"

	def validate_warehouse_company(self):
		if self.warehouse and self.company:
			warehouse_company = frappe.get_cached_value("Warehouse", self.warehouse, "company")
			if warehouse_company != self.company:
				frappe.throw(_("Warehouse does not belong to selected company"))

	def validate_warehouse_not_reserved_or_unreserved(self):
		if not self.warehouse:
			return
		wh_name = frappe.get_cached_value("Warehouse", self.warehouse, "warehouse_name")
		wh_name_lower = (wh_name or "").strip().lower()
		if wh_name_lower.startswith("reserved wh") or wh_name_lower.startswith("unreserved wh"):
			frappe.throw(_("Source warehouse cannot be Reserved WH or Unreserved WH. "
				"Select an available stock warehouse instead."))

	def set_reserved_and_unreserved_warehouses(self):
		if not self.company:
			return
		abbr = frappe.get_cached_value("Company", self.company, "abbr")
		self.reserved_warehouse = f"Reserved WH - {abbr}"
		self.unreserved_warehouse = f"Unreserved WH - {abbr}"

	def before_submit(self):
		self.validate_items()
		self.status = "Reserved"

	def on_submit(self):
		self.update_stock_ledger(reserve=True)

	def on_cancel(self):
		self.status = "Cancelled"
		self.cancel_reservation_stock_entries()
		self.db_update()

	def validate_items(self):
		if not self.items:
			frappe.throw(_("Please add at least one item to reserve"))

		for row in self.items:
			if not row.qty:
				frappe.throw(_("Row #{0}: Reserve Qty is mandatory").format(row.idx))
			if flt(row.qty) <= 0:
				frappe.throw(_("Row #{0}: Reserve Qty must be greater than 0").format(row.idx))

	def get_reserved_warehouse(self):
		company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
		reserved_wh = f"Reserved WH - {company_abbr}"
		if not frappe.db.exists("Warehouse", reserved_wh):
			frappe.throw(
				_("Reserved Warehouse '{0}' not found for company {1}").format(reserved_wh, self.company)
			)
		return reserved_wh

	def update_stock_ledger(self, reserve=True):
		if not self.warehouse or not self.company or not self.items:
			return

		if reserve:
			reserved_warehouse = self.get_reserved_warehouse()
			for row in self.items:
				if row.stock_entry:
					continue
				basic_rate = self.get_valuation_rate(row.item, self.warehouse)
				stock_entry = frappe.new_doc("Stock Entry")
				stock_entry.stock_entry_type = "Material Transfer"
				stock_entry.purpose = "Material Transfer"
				stock_entry.company = self.company
				item_data = {
					"item_code": row.item,
					"s_warehouse": self.warehouse,
					"t_warehouse": reserved_warehouse,
					"qty": row.qty,
					"basic_rate": basic_rate,
				}
				if row.batch_no:
					item_data["batch_no"] = row.batch_no
				stock_entry.append("items", item_data)
				stock_entry.flags.ignore_permissions = True
				stock_entry.flags.ignore_links = True
				stock_entry.submit()
				frappe.db.set_value("Stock Reservation Item", row.name, "stock_entry", stock_entry.name)

	def cancel_reservation_stock_entries(self):
		for row in self.items:
			if row.stock_entry:
				try:
					se = frappe.get_doc("Stock Entry", row.stock_entry)
					se.flags.ignore_permissions = True
					se.flags.ignore_links = True
					se.cancel()
					frappe.db.set_value("Stock Reservation Item", row.name, "stock_entry", "")
				except Exception:
					frappe.log_error(
						f"Failed to cancel Stock Entry {row.stock_entry} for Stock Reservation Item {row.name}"
					)

	def get_valuation_rate(self, item_code, warehouse):
		bin_rate = frappe.db.get_value(
			"Bin", {"item_code": item_code, "warehouse": warehouse}, "valuation_rate"
		)
		if bin_rate:
			return flt(bin_rate)
		return flt(frappe.db.get_value("Item", item_code, "valuation_rate") or 0)

	@frappe.whitelist()
	def get_swastik_breakdown(self):
		items_raw = frappe.form_dict.get("items") or [row.item for row in self.items if row.item]

		if isinstance(items_raw, str):
			items = json.loads(items_raw)
		else:
			items = items_raw

		if not items:
			return []

		companies = frappe.get_all("Company", pluck="name")
		company_abbrs = {c: frappe.get_cached_value("Company", c, "abbr") for c in companies}

		rows = []
		for item in items:
			row = {"item": item}
			total = 0
			for company, abbr in company_abbrs.items():
				wh = f"Reserved WH - {abbr}"
				qty = flt(frappe.db.get_value("Bin", {"item_code": item, "warehouse": wh}, "actual_qty") or 0)
				row[company] = qty
				total += qty
			row["total"] = total
			row["item_name"] = frappe.get_cached_value("Item", item, "item_name") or item
			rows.append(row)

		return rows

	@frappe.whitelist()
	def get_release_breakdown(self):
		items_raw = frappe.form_dict.get("items") or [row.item for row in self.items if row.item]

		if isinstance(items_raw, str):
			items = json.loads(items_raw)
		else:
			items = items_raw

		if not items:
			return []

		companies = frappe.get_all("Company", pluck="name")
		company_abbrs = {c: frappe.get_cached_value("Company", c, "abbr") for c in companies}

		rows = []
		for item in items:
			row = {"item": item}
			total = 0
			for company, abbr in company_abbrs.items():
				wh = f"Unreserved WH - {abbr}"
				qty = flt(frappe.db.get_value("Bin", {"item_code": item, "warehouse": wh}, "actual_qty") or 0)
				row[company] = qty
				total += qty
			row["total"] = total
			row["item_name"] = frappe.get_cached_value("Item", item, "item_name") or item
			rows.append(row)

		return rows

	@frappe.whitelist()
	def get_item_reservation_data(self, item=None, source_warehouse=None, reserved_warehouse=None):
		result = {"available_qty": 0, "already_reserved_qty": 0}

		if item and source_warehouse:
			result["available_qty"] = flt(
				frappe.db.get_value("Bin", {"item_code": item, "warehouse": source_warehouse}, "actual_qty") or 0
			)

		if item and reserved_warehouse:
			result["already_reserved_qty"] = flt(
				frappe.db.get_value("Bin", {"item_code": item, "warehouse": reserved_warehouse}, "actual_qty") or 0
			)

		return result
