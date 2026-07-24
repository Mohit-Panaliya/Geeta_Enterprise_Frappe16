import frappe
from frappe.utils import flt, today, getdate, get_first_day


def _get_filters():
    company = frappe.form_dict.get("company", "All") or "All"
    item = frappe.form_dict.get("item", "All") or "All"
    return company, item


def _parse_csv(val):
    if not val or val == "All":
        return []
    return [v.strip() for v in val.split(",") if v.strip() and v.strip() != "All"]


def _co_filter(alias="w"):
    company, _ = _get_filters()
    vals = _parse_csv(company)
    if vals:
        placeholders = ", ".join(["%s"] * len(vals))
        return f"AND {alias}.company IN ({placeholders})", vals
    return "", []


def _item_filter(alias="b"):
    _, item = _get_filters()
    vals = _parse_csv(item)
    if vals:
        placeholders = ", ".join(["%s"] * len(vals))
        return f"AND {alias}.item_code IN ({placeholders})", vals
    return "", []


@frappe.whitelist()
def get_stock_kpis():
    company, item = _get_filters()
    co_f, co_a = _co_filter()
    it_f, it_a = _item_filter()

    UOM_JOIN = "LEFT JOIN `tabUOM Conversion Detail` ucd ON ucd.parent = b.item_code AND ucd.uom = 'Litre'"
    UOM_SEL = "COALESCE(ucd.conversion_factor, 1.0)"

    avail = frappe.db.sql(
        """SELECT COALESCE(SUM(b.actual_qty), 0) as nos,
            COALESCE(SUM(b.actual_qty * {f}), 0) as litres,
            COALESCE(SUM(b.stock_value), 0) as val
        FROM `tabBin` b JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE w.name LIKE 'Available WH - %%' AND b.actual_qty > 0 """.format(f=UOM_SEL, j=UOM_JOIN)
        + co_f + it_f,
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    reserved = frappe.db.sql(
        """SELECT COALESCE(SUM(b.actual_qty), 0) as nos,
            COALESCE(SUM(b.actual_qty * {f}), 0) as litres,
            COALESCE(SUM(b.stock_value), 0) as val
        FROM `tabBin` b JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE w.name LIKE 'Reserved WH - %%' AND b.actual_qty > 0 """.format(f=UOM_SEL, j=UOM_JOIN)
        + co_f + it_f,
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    neg = frappe.db.sql(
        """SELECT COUNT(*) as cnt FROM `tabBin` b
        JOIN `tabWarehouse` w ON w.name = b.warehouse
        WHERE b.actual_qty < 0 """
        + co_f + it_f,
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    items_count = frappe.db.sql(
        """SELECT COUNT(DISTINCT b.item_code) as cnt FROM `tabBin` b
        JOIN `tabWarehouse` w ON w.name = b.warehouse
        WHERE b.actual_qty > 0 """
        + co_f + it_f,
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    wh_count = frappe.db.sql(
        """SELECT COUNT(DISTINCT w.name) as cnt FROM `tabBin` b
        JOIN `tabWarehouse` w ON w.name = b.warehouse
        WHERE b.actual_qty > 0 """
        + co_f + it_f,
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    unreserved = frappe.db.sql(
        """SELECT COALESCE(SUM(b.actual_qty), 0) as nos,
            COALESCE(SUM(b.actual_qty * {f}), 0) as litres
        FROM `tabBin` b JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE w.name LIKE 'Unreserved WH - %%' AND b.actual_qty > 0 """.format(f=UOM_SEL, j=UOM_JOIN)
        + co_f + it_f,
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    release_cond = "sr.docstatus = 1"
    release_args = []
    if company != "All":
        companies = [c.strip() for c in company.split(",") if c.strip()]
        if companies:
            release_cond += " AND sr.company IN ({})".format(",".join(["%s"] * len(companies)))
            release_args.extend(companies)
    if item != "All":
        items = [i.strip() for i in item.split(",") if i.strip()]
        if items:
            placeholders = ",".join(["%s"] * len(items))
            release_cond += " AND sri.item IN ({})".format(placeholders)
            release_args.extend(items)

    released = frappe.db.sql(
        """SELECT COALESCE(SUM(sr.total_release_qty), 0) as qty, COUNT(DISTINCT sr.name) as cnt
        FROM `tabStock Release` sr
        {item_join}
        WHERE {cond}
    """.format(
            item_join="INNER JOIN `tabStock Release Item` sri ON sri.parent = sr.name" if item != "All" else "",
            cond=release_cond
        ),
        tuple(release_args) if release_args else (),
        as_dict=True,
    )

    a_nos = flt(avail[0].nos) if avail else 0
    a_lit = flt(avail[0].litres) if avail else 0
    a_val = flt(avail[0].val) if avail else 0
    r_nos = flt(reserved[0].nos) if reserved else 0
    r_lit = flt(reserved[0].litres) if reserved else 0
    r_val = flt(reserved[0].val) if reserved else 0
    u_nos = flt(unreserved[0].nos) if unreserved else 0
    u_lit = flt(unreserved[0].litres) if unreserved else 0

    return {
        "available_nos": a_nos,
        "available_qty": a_lit,
        "available_value": a_val,
        "reserved_nos": r_nos,
        "reserved_qty": r_lit,
        "reserved_value": r_val,
        "unreserved_nos": u_nos,
        "unreserved_qty": u_lit,
        "released_qty": flt(released[0].qty) if released else 0,
        "release_count": int(released[0].cnt) if released else 0,
        "total_stock": a_lit + r_lit + u_lit,
        "total_nos": a_nos + r_nos + u_nos,
        "total_value": a_val + r_val,
        "negative_count": int(neg[0].cnt) if neg else 0,
        "items_count": int(items_count[0].cnt) if items_count else 0,
        "warehouse_count": int(wh_count[0].cnt) if wh_count else 0,
        "utilization_pct": ((r_lit / (a_lit + r_lit)) * 100) if (a_lit + r_lit) > 0 else 0,
    }


@frappe.whitelist()
def get_stock_by_company():
    company, item = _get_filters()
    co_f, co_a = _co_filter()
    it_f, it_a = _item_filter()
    UOM_JOIN = "LEFT JOIN `tabUOM Conversion Detail` ucd ON ucd.parent = b.item_code AND ucd.uom = 'Litre'"
    UOM_SEL = "COALESCE(ucd.conversion_factor, 1.0)"

    sql = """SELECT w.company,
            SUM(CASE WHEN w.name LIKE 'Available WH - %%' THEN b.actual_qty ELSE 0 END) as avail_nos,
            SUM(CASE WHEN w.name LIKE 'Available WH - %%' THEN b.actual_qty * {f} ELSE 0 END) as avail_qty,
            SUM(CASE WHEN w.name LIKE 'Available WH - %%' THEN b.stock_value ELSE 0 END) as avail_val,
            SUM(CASE WHEN w.name LIKE 'Reserved WH - %%' THEN b.actual_qty ELSE 0 END) as reserved_nos,
            SUM(CASE WHEN w.name LIKE 'Reserved WH - %%' THEN b.actual_qty * {f} ELSE 0 END) as reserved_qty,
            SUM(CASE WHEN w.name LIKE 'Reserved WH - %%' THEN b.stock_value ELSE 0 END) as reserved_val,
            SUM(CASE WHEN w.name LIKE 'Unreserved WH - %%' THEN b.actual_qty ELSE 0 END) as unreserved_nos,
            SUM(CASE WHEN w.name LIKE 'Unreserved WH - %%' THEN b.actual_qty * {f} ELSE 0 END) as unreserved_qty,
            SUM(CASE WHEN w.name LIKE 'Unreserved WH - %%' THEN b.stock_value ELSE 0 END) as unreserved_val,
            SUM(b.actual_qty) as total_nos,
            SUM(b.actual_qty * {f}) as total_qty,
            SUM(b.stock_value) as total_value,
            COUNT(DISTINCT b.item_code) as item_count
        FROM `tabBin` b
        JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE b.actual_qty > 0 """.format(f=UOM_SEL, j=UOM_JOIN)
    sql += co_f + it_f + " GROUP BY w.company ORDER BY total_value DESC"
    return frappe.db.sql(sql, tuple(co_a) + tuple(it_a), as_dict=True)


@frappe.whitelist()
def get_stock_by_warehouse():
    company, item = _get_filters()
    co_f, co_a = _co_filter()
    it_f, it_a = _item_filter()

    UOM_JOIN = "LEFT JOIN `tabUOM Conversion Detail` ucd ON ucd.parent = b.item_code AND ucd.uom = 'Litre'"
    UOM_SEL = "COALESCE(ucd.conversion_factor, 1.0)"

    # Get warehouse-level summary
    sql = """SELECT w.name as warehouse, w.company, w.warehouse_type,
            SUM(b.actual_qty) as total_nos,
            SUM(b.actual_qty * {f}) as total_qty,
            SUM(b.stock_value) as total_value,
            COUNT(DISTINCT b.item_code) as item_count
        FROM `tabBin` b
        JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE b.actual_qty != 0 AND w.name LIKE '%% WH - %%' """.format(f=UOM_SEL, j=UOM_JOIN)
    sql += co_f + it_f + " GROUP BY w.name ORDER BY w.company, total_value DESC"
    warehouses = frappe.db.sql(sql, tuple(co_a) + tuple(it_a), as_dict=True)

    # Get item details per warehouse
    wh_names = [w.warehouse for w in warehouses]
    if wh_names:
        placeholders = ", ".join(["%s"] * len(wh_names))
        items = frappe.db.sql(
            f"""SELECT b.warehouse, b.item_code, b.actual_qty as qty, b.stock_value as value,
                b.valuation_rate,
                COALESCE((
                    SELECT ucd.conversion_factor
                    FROM `tabUOM Conversion Detail` ucd
                    WHERE ucd.parent = b.item_code AND ucd.uom = 'Litre'
                ), 1.0) as litre_factor
            FROM `tabBin` b
            WHERE b.warehouse IN ({placeholders}) AND b.actual_qty != 0 {it_f}
            ORDER BY b.warehouse, b.stock_value DESC""",
            tuple(wh_names) + tuple(it_a), as_dict=True,
        )
    else:
        items = []

    # Group items by warehouse
    wh_items = {}
    for it in items:
        wh = it.warehouse
        if wh not in wh_items:
            wh_items[wh] = []
        wh_items[wh].append({
            "item_code": it.item_code,
            "qty": flt(it.qty),
            "litres": flt(it.qty) * flt(it.litre_factor or 1),
            "litre_factor": flt(it.litre_factor or 1),
            "value": flt(it.value),
            "rate": flt(it.valuation_rate),
        })

    # Attach items to warehouses
    for wh in warehouses:
        wh["items"] = wh_items.get(wh.warehouse, [])

    return warehouses


@frappe.whitelist()
def get_stock_by_item():
    company, item = _get_filters()
    co_f, co_a = _co_filter()
    it_f, it_a = _item_filter()
    UOM_JOIN = "LEFT JOIN `tabUOM Conversion Detail` ucd ON ucd.parent = b.item_code AND ucd.uom = 'Litre'"
    UOM_SEL = "COALESCE(ucd.conversion_factor, 1.0)"

    sql = """SELECT b.item_code, w.company,
            SUM(b.actual_qty) as nos,
            SUM(b.actual_qty * {f}) as litres,
            SUM(b.stock_value) as value
        FROM `tabBin` b
        JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE b.actual_qty != 0 """.format(f=UOM_SEL, j=UOM_JOIN)
    sql += co_f + it_f + " GROUP BY b.item_code, w.company ORDER BY b.item_code, value DESC"
    data = frappe.db.sql(sql, tuple(co_a) + tuple(it_a), as_dict=True)

    items = {}
    for row in data:
        ic = row.item_code
        if ic not in items:
            items[ic] = {"item_code": ic, "companies": {}, "total_nos": 0, "total_litres": 0, "total_value": 0}
        co = row.company
        items[ic]["companies"][co] = {"nos": flt(row.nos), "litres": flt(row.litres), "value": flt(row.value)}
        items[ic]["total_nos"] += flt(row.nos)
        items[ic]["total_litres"] += flt(row.litres)
        items[ic]["total_value"] += flt(row.value)

    return sorted(items.values(), key=lambda x: x["total_value"], reverse=True)


@frappe.whitelist()
def get_swastik_detail():
    company, item = _get_filters()
    co_f, co_a = _co_filter()
    it_f, it_a = _item_filter()
    UOM_JOIN = "LEFT JOIN `tabUOM Conversion Detail` ucd ON ucd.parent = b.item_code AND ucd.uom = 'Litre'"
    UOM_SEL = "COALESCE(ucd.conversion_factor, 1.0)"

    total = frappe.db.sql(
        """SELECT COALESCE(SUM(b.actual_qty), 0) as nos,
            COALESCE(SUM(b.actual_qty * {f}), 0) as qty,
            COALESCE(SUM(b.stock_value), 0) as val
        FROM `tabBin` b JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE w.name LIKE 'Reserved WH - %%' AND b.actual_qty > 0 """.format(f=UOM_SEL, j=UOM_JOIN)
        + co_f + it_f,
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    by_company = frappe.db.sql(
        """SELECT w.company,
            SUM(b.actual_qty) as nos,
            SUM(b.actual_qty * {f}) as qty,
            SUM(b.stock_value) as val
        FROM `tabBin` b JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE w.name LIKE 'Reserved WH - %%' AND b.actual_qty > 0 """.format(f=UOM_SEL, j=UOM_JOIN)
        + co_f + it_f + """
        GROUP BY w.company ORDER BY val DESC""",
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    by_item = frappe.db.sql(
        """SELECT b.item_code,
            SUM(b.actual_qty) as nos,
            SUM(b.actual_qty * {f}) as qty,
            SUM(b.stock_value) as val
        FROM `tabBin` b JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE w.name LIKE 'Reserved WH - %%' AND b.actual_qty > 0 """.format(f=UOM_SEL, j=UOM_JOIN)
        + co_f + it_f + """
        GROUP BY b.item_code ORDER BY val DESC""",
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    detail = frappe.db.sql(
        """SELECT w.company, b.item_code, b.warehouse, b.actual_qty as qty, b.stock_value as val,
            {f} as litre_factor
        FROM `tabBin` b JOIN `tabWarehouse` w ON w.name = b.warehouse {j}
        WHERE w.name LIKE 'Reserved WH - %%' AND b.actual_qty > 0 """.format(f=UOM_SEL, j=UOM_JOIN)
        + co_f + it_f + """
        ORDER BY w.company, b.item_code""",
        tuple(co_a) + tuple(it_a), as_dict=True,
    )

    return {
        "total_nos": flt(total[0].nos) if total else 0,
        "total_qty": flt(total[0].qty) if total else 0,
        "total_value": flt(total[0].val) if total else 0,
        "companies_count": len(by_company),
        "items_count": len(by_item),
        "by_company": by_company,
        "by_item": by_item,
        "detail": detail,
    }


@frappe.whitelist()
def get_negative_stock():
    company, item = _get_filters()
    co_f, co_a = _co_filter()
    it_f, it_a = _item_filter()

    return frappe.db.sql(
        """SELECT w.company, w.name as warehouse, b.item_code, b.actual_qty, b.stock_value,
            COALESCE((
                SELECT ucd.conversion_factor
                FROM `tabUOM Conversion Detail` ucd
                WHERE ucd.parent = b.item_code AND ucd.uom = 'Litre'
            ), 1.0) as litre_factor
        FROM `tabBin` b JOIN `tabWarehouse` w ON w.name = b.warehouse
        WHERE b.actual_qty < 0 """
        + co_f + it_f + """
        ORDER BY w.company, b.actual_qty ASC LIMIT 30""",
        tuple(co_a) + tuple(it_a), as_dict=True,
    )
