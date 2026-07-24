import frappe
from frappe import _
from frappe.utils import flt


def handle_stock_entry_submit(doc, method):
    pass


def handle_stock_entry_cancel(doc, method):
    pass


def validate_reserved_wh_sale(doc, method):
    for item in doc.get("items", []):
        warehouse = item.get("warehouse") or item.get("s_warehouse") or ""
        if not warehouse:
            continue
        wh_name = frappe.get_cached_value("Warehouse", warehouse, "warehouse_name") or ""
        if wh_name.startswith("Reserved WH"):
            frappe.throw(_(
                "Row #{0}: Cannot sell from Reserved Warehouse '{1}'. "
                "Unreserve the stock first using Unreserve action."
            ).format(item.idx, warehouse))


def validate_unreserved_wh_stock(doc, method):
    for item in doc.get("items", []):
        warehouse = item.get("warehouse") or item.get("s_warehouse") or ""
        if not warehouse:
            continue
        wh_name = frappe.get_cached_value("Warehouse", warehouse, "warehouse_name") or ""
        if not wh_name.startswith("Unreserved WH"):
            continue

        qty = flt(item.get("qty") or item.get("transfer_qty") or 0)
        actual_qty = flt(frappe.db.get_value(
            "Bin", {"item_code": item.item_code, "warehouse": warehouse}, "actual_qty"
        ) or 0)

        if qty > actual_qty:
            frappe.throw(_(
                "Row #{0}: Cannot sell {1} units from Unreserved Warehouse '{2}'. "
                "Only {3} units available. Negative stock from Unreserved is not allowed."
            ).format(item.idx, qty, warehouse, actual_qty))
