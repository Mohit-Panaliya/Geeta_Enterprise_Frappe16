import frappe
import json
from frappe import _
from frappe.utils import flt, nowdate


class StockRelease(frappe.model.document.Document):
	def validate(self):
		self.set_missing_values()
		self.validate_items()

	def set_missing_values(self):
		if not self.posting_date:
			self.posting_date = nowdate()
		if not self.status:
			self.status = "Draft"
		self.total_release_qty = sum(flt(d.qty) for d in self.items)

	def validate_items(self):
		if not self.items:
			frappe.throw(_("At least one release item is required"))

		company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
		reserved_wh = f"Reserved WH - {company_abbr}"
		unreserved_wh = f"Unreserved WH - {company_abbr}"

		if not frappe.db.exists("Warehouse", reserved_wh):
			frappe.throw(_("Reserved Warehouse '{0}' not found for company {1}").format(reserved_wh, self.company))
		if not frappe.db.exists("Warehouse", unreserved_wh):
			frappe.throw(_("Unreserved Warehouse '{0}' not found for company {1}").format(unreserved_wh, self.company))

		for item in self.items:
			if flt(item.qty) <= 0:
				frappe.throw(_("Qty must be greater than 0 for row {0}").format(item.idx))

			available = flt(frappe.db.get_value(
				"Bin", {"item_code": item.item, "warehouse": reserved_wh}, "actual_qty"
			) or 0)

			if flt(item.qty) > available:
				frappe.throw(_(
					"Item {0}: Cannot release {1} units. Only {2} units available in {3}."
				).format(item.item, item.qty, available, reserved_wh))

			item.reserved_warehouse = reserved_wh
			item.unreserved_warehouse = unreserved_wh

	def before_submit(self):
		self.status = "Released"

	def on_submit(self):
		self.create_stock_entries()

	def on_cancel(self):
		self.cancel_stock_entries()
		self.status = "Cancelled"

	def create_stock_entries(self):
		company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
		reserved_wh = f"Reserved WH - {company_abbr}"
		unreserved_wh = f"Unreserved WH - {company_abbr}"

		for item in self.items:
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Transfer"
			se.purpose = "Material Transfer"
			se.company = self.company
			se.posting_date = self.posting_date

			se.append("items", {
				"item_code": item.item,
				"s_warehouse": reserved_wh,
				"t_warehouse": unreserved_wh,
				"qty": item.qty,
				"basic_rate": self.get_valuation_rate(item.item, reserved_wh),
				"uom": item.stock_uom,
			})

			se.flags.ignore_permissions = True
			se.flags.ignore_links = True
			se.submit()

			item.db_set("stock_entry", se.name)

	def cancel_stock_entries(self):
		for item in self.items:
			if item.stock_entry:
				se = frappe.get_doc("Stock Entry", item.stock_entry)
				se.flags.ignore_permissions = True
				se.cancel()
				item.db_set("stock_entry", "")

	def get_valuation_rate(self, item_code, warehouse):
		bin_rate = frappe.db.get_value(
			"Bin", {"item_code": item_code, "warehouse": warehouse}, "valuation_rate"
		)
		if bin_rate:
			return flt(bin_rate)
		return flt(frappe.db.get_value("Item", item_code, "valuation_rate") or 0)

	@frappe.whitelist()
	def get_item_release_data(self, item=None, reserved_warehouse=None, unreserved_warehouse=None):
		result = {"reserved_qty": 0, "already_released_qty": 0}

		if item and reserved_warehouse:
			result["reserved_qty"] = flt(
				frappe.db.get_value("Bin", {"item_code": item, "warehouse": reserved_warehouse}, "actual_qty") or 0
			)

		if item and unreserved_warehouse:
			result["already_released_qty"] = flt(
				frappe.db.get_value("Bin", {"item_code": item, "warehouse": unreserved_warehouse}, "actual_qty") or 0
			)

		return result

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
