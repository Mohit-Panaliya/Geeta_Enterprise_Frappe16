import frappe
from frappe.utils import today, nowdate, flt

COMPANIES = {
    "Geeta Enterprise": "GE",
    "Global Export": "GEX",
    "Shubham Enterprise": "SHE",
    "Swastik": "SWK",
}


def _upsert_uom_conversion(item_code, litre_conversion):
    """Add/update Litre UOM conversion on an existing Item, ensuring Nos exists."""
    item = frappe.get_doc("Item", item_code)
    found_litre = False
    found_nos = False
    for row in item.get("uoms", []):
        if row.uom == "Litre":
            row.conversion_factor = litre_conversion
            found_litre = True
        if row.uom == "Nos":
            found_nos = True
    if not found_litre:
        item.append("uoms", {"uom": "Litre", "conversion_factor": litre_conversion})
    if not found_nos:
        item.append("uoms", {"uom": "Nos", "conversion_factor": 1})
    item.save(ignore_permissions=True)


def setup_master_data():
    """Create all master data needed for oil distribution testing."""
    print("=" * 60)
    print("SETTING UP MASTER DATA")
    print("=" * 60)

    # 1. Companies
    print("\n--- Companies ---")
    for company_name, abbr in COMPANIES.items():
        if not frappe.db.exists("Company", company_name):
            doc = frappe.get_doc({
                "doctype": "Company",
                "company_name": company_name,
                "abbr": abbr,
                "default_currency": "INR",
                "country": "India",
            })
            doc.insert(ignore_permissions=True)
            print(f"  Created: {company_name} ({abbr})")
    frappe.db.commit()

    # 2. Warehouses
    print("\n--- Warehouses ---")
    for company_name, abbr in COMPANIES.items():
        for wh_type in ["Available", "Reserved", "Unreserved"]:
            wh_name = f"{wh_type} WH - {abbr}"
            if not frappe.db.exists("Warehouse", wh_name):
                doc = frappe.get_doc({
                    "doctype": "Warehouse",
                    "warehouse_name": f"{wh_type} WH",
                    "company": company_name,
                })
                doc.insert(ignore_permissions=True)
                print(f"  Created: {wh_name}")
    frappe.db.commit()

    # 3. HSN Codes
    print("\n--- HSN Codes ---")
    for hsn in ["271019"]:
        if not frappe.db.exists("GST HSN Code", hsn):
            frappe.get_doc({"doctype": "GST HSN Code", "hsn_code": hsn, "description": "Engine Oil", "uom": "Nos"}).insert(ignore_permissions=True)
            print(f"  Created: {hsn}")
    frappe.db.commit()

    # 4. Items with categories, valuation rates + UOM conversion to Litre
    print("\n--- Items ---")
    PRODUCT_CATALOG = [
        # code, name, hsn, val_rate, litre_per_unit, category, sub_category
        # ── 2 Wheeler ──
        ("2W-ENGINE-20W40", "2 Wheeler Engine Oil 20W-40", "271019", 350, 0.4, "2 Wheeler", "Mass"),
        ("2W-ENGINE-10W30", "2 Wheeler Engine Oil 10W-30", "271019", 420, 0.4, "2 Wheeler", "Premium"),
        ("2W-ENGINE-5W30",  "2 Wheeler Engine Oil 5W-30",  "271019", 480, 0.4, "2 Wheeler", "Premium"),
        # ── 4 Wheeler ──
        ("4W-ENGINE-20W50", "4 Wheeler Engine Oil 20W-50", "271019", 480, 1.0, "4 Wheeler", "Mass"),
        ("4W-ENGINE-10W40", "4 Wheeler Engine Oil 10W-40", "271019", 520, 1.0, "4 Wheeler", "Mass"),
        ("4W-ENGINE-5W30",  "4 Wheeler Engine Oil 5W-30",  "271019", 650, 1.0, "4 Wheeler", "Premium"),
        ("4W-ENGINE-0W20",  "4 Wheeler Engine Oil 0W-20",  "271019", 750, 1.0, "4 Wheeler", "Premium"),
        # ── Truck ──
        ("TRK-ENGINE-20W50", "Truck Engine Oil 20W-50", "271019", 1800, 5.0, "Truck", "Mass"),
        ("TRK-ENGINE-15W40", "Truck Engine Oil 15W-40", "271019", 2200, 5.0, "Truck", "Premium"),
        ("TRK-ENGINE-10W30", "Truck Engine Oil 10W-30", "271019", 2500, 5.0, "Truck", "Premium"),
        # ── Industry ──
        ("IND-HYDRAULIC-68", "Hydraulic Oil 68", "271019", 3500, 20.0, "Industry", "Mass"),
        ("IND-HYDRAULIC-46", "Hydraulic Oil 46", "271019", 3200, 20.0, "Industry", "Mass"),
        ("IND-GEAR-220",     "Industrial Gear Oil 220", "271019", 5200, 20.0, "Industry", "Premium"),
        ("IND-TURBINE-32",   "Turbine Oil 32", "271019", 4800, 20.0, "Industry", "Premium"),
        # ── Farming ──
        ("FARM-ENGINE-10W30", "Tractor Engine Oil 10W-30", "271019", 1500, 5.0, "Farming", "Mass"),
        ("FARM-HYDRAULIC-32", "Tractor Hydraulic Oil 32",  "271019", 2000, 5.0, "Farming", "Premium"),
        # ── Legacy items (reassigned) ──
        ("ENGINE-10W30", "Engine Oil 10W-30", "271019", 450, 1.0, "4 Wheeler", "Mass"),
        ("ENGINE-15W40", "Engine Oil 15W-40", "271019", 520, 1.0, "Truck", "Premium"),
        ("ENGINE-20W50", "Engine Oil 20W-50", "271019", 480, 1.0, "Truck", "Mass"),
        ("ENGINE-5W30",  "Engine Oil 5W-30",  "271019", 600, 1.0, "4 Wheeler", "Premium"),
    ]

    for code, name, hsn, val_rate, litre_per_unit, cat, subcat in PRODUCT_CATALOG:
        conversion = 1.0 / litre_per_unit if litre_per_unit else 1.0

        if not frappe.db.exists("Item", code):
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": code,
                "item_name": name,
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 1,
                "gst_hsn_code": hsn,
                "valuation_rate": val_rate,
                "product_category": cat,
                "product_sub_category": subcat,
                "uoms": [
                    {"uom": "Nos", "conversion_factor": 1},
                    {"uom": "Litre", "conversion_factor": conversion},
                ],
            })
            doc.insert(ignore_permissions=True)
            print(f"  Created: {code} ({cat}/{subcat}, {val_rate}/u, {litre_per_unit}L/pc)")
        else:
            frappe.db.set_value("Item", code, "valuation_rate", val_rate)
            frappe.db.set_value("Item", code, "product_category", cat)
            frappe.db.set_value("Item", code, "product_sub_category", subcat)
            _upsert_uom_conversion(code, conversion)
            print(f"  Updated: {code} → {cat}/{subcat}")
    frappe.db.commit()

    # 5. Inter-Company Supplier/Customer Pairs
    print("\n--- Inter-Company Links ---")
    pairs = [
        ("Geeta Enterprise", "Global Export"),
        ("Geeta Enterprise", "Shubham Enterprise"),
        ("Global Export", "Geeta Enterprise"),
        ("Global Export", "Shubham Enterprise"),
        ("Shubham Enterprise", "Geeta Enterprise"),
        ("Shubham Enterprise", "Global Export"),
    ]
    for supplier_co, customer_co in pairs:
        sup_abbr = COMPANIES[supplier_co]
        cust_abbr = COMPANIES[customer_co]
        sup_name = f"{sup_abbr} Supplier"
        if not frappe.db.exists("Supplier", sup_name):
            sup = frappe.get_doc({
                "doctype": "Supplier", "supplier_name": sup_name,
                "supplier_group": "Local", "is_internal_supplier": 1,
                "represents_company": supplier_co,
            })
            sup.append("companies", {"company": customer_co})
            sup.insert(ignore_permissions=True)
            print(f"  Created Supplier: {sup_name}")
        else:
            # Ensure allowed company is set
            sup = frappe.get_doc("Supplier", sup_name)
            existing_companies = [d.company for d in sup.get("companies", [])]
            if customer_co not in existing_companies:
                sup.append("companies", {"company": customer_co})
                sup.save(ignore_permissions=True)

        cust_name = f"{cust_abbr} Customer"
        if not frappe.db.exists("Customer", cust_name):
            cust = frappe.get_doc({
                "doctype": "Customer", "customer_name": cust_name,
                "customer_group": "Commercial", "territory": "India",
                "is_internal_customer": 1, "represents_company": customer_co,
            })
            cust.append("companies", {"company": supplier_co})
            cust.insert(ignore_permissions=True)
            print(f"  Created Customer: {cust_name}")
        else:
            # Ensure allowed company is set
            cust = frappe.get_doc("Customer", cust_name)
            existing_companies = [d.company for d in cust.get("companies", [])]
            if supplier_co not in existing_companies:
                cust.append("companies", {"company": supplier_co})
                cust.save(ignore_permissions=True)
    frappe.db.commit()

    # 6. Price Lists (Standard Selling + Standard Buying with both flags)
    print("\n--- Price Lists ---")
    for pl_name in ["Standard Selling", "Standard Buying"]:
        if frappe.db.exists("Price List", pl_name):
            frappe.db.set_value("Price List", pl_name, {"selling": 1, "buying": 1, "enabled": 1})
            print(f"  Updated: {pl_name} (selling=1, buying=1)")

    # Set default price lists on Selling/Buying Settings
    if frappe.db.exists("Selling Settings"):
        frappe.db.set_value("Selling Settings", None, "selling_price_list", "Standard Selling")
    if frappe.db.exists("Buying Settings"):
        frappe.db.set_value("Buying Settings", None, "buying_price_list", "Standard Buying")
    frappe.db.commit()
    print("  Set default price lists on Selling/Buying Settings")

    # 7. Transfer Settings (singleton)
    print("\n--- Transfer Settings ---")
    ts = frappe.get_single("Transfer Settings")
    ts.company = "Geeta Enterprise"
    ts.default_source_warehouse = "Available WH - GE"
    ts.default_target_warehouse = "Available WH - GE"
    ts.auto_create_intercompany_docs = 1
    ts.save(ignore_permissions=True)
    print("  Saved Transfer Settings for Geeta Enterprise")
    frappe.db.commit()

    # 7. Fiscal Year 2026
    print("\n--- Fiscal Year ---")
    if not frappe.db.exists("Fiscal Year", {"year": "2026"}):
        frappe.get_doc({
            "doctype": "Fiscal Year",
            "year": "2026",
            "year_start_date": "2026-04-01",
            "year_end_date": "2027-03-31",
        }).insert(ignore_permissions=True)
        print("  Created Fiscal Year 2026")
    else:
        print("  Exists Fiscal Year 2026")
    frappe.db.commit()

    # 8. Enable Allow Negative Stock
    print("\n--- Stock Settings ---")
    ss = frappe.get_single("Stock Settings")
    if not ss.allow_negative_stock:
        ss.allow_negative_stock = 1
        ss.save(ignore_permissions=True)
        print("  Enabled Allow Negative Stock")
    else:
        print("  Allow Negative Stock already enabled")
    frappe.db.commit()

    # 9. Opening Stock (Material Receipt with valuation rate)
    print("\n--- Opening Stock ---")
    stock_data = [
        # Geeta Enterprise
        ("Geeta Enterprise", "Available WH - GE", "ENGINE-10W30", 500, 450),
        ("Geeta Enterprise", "Available WH - GE", "ENGINE-15W40", 300, 520),
        ("Geeta Enterprise", "Available WH - GE", "ENGINE-20W50", 200, 480),
        ("Geeta Enterprise", "Available WH - GE", "ENGINE-5W30", 100, 600),
        ("Geeta Enterprise", "Available WH - GE", "2W-ENGINE-20W40", 300, 350),
        ("Geeta Enterprise", "Available WH - GE", "2W-ENGINE-10W30", 200, 420),
        ("Geeta Enterprise", "Available WH - GE", "4W-ENGINE-10W40", 250, 520),
        ("Geeta Enterprise", "Available WH - GE", "TRK-ENGINE-15W40", 100, 2200),
        ("Geeta Enterprise", "Available WH - GE", "IND-HYDRAULIC-68", 50, 3500),
        ("Geeta Enterprise", "Available WH - GE", "FARM-ENGINE-10W30", 80, 1500),
        # Global Export
        ("Global Export", "Available WH - GEX", "ENGINE-10W30", 200, 450),
        ("Global Export", "Available WH - GEX", "ENGINE-20W50", 150, 480),
        ("Global Export", "Available WH - GEX", "2W-ENGINE-20W40", 150, 350),
        ("Global Export", "Available WH - GEX", "4W-ENGINE-5W30", 80, 650),
        ("Global Export", "Available WH - GEX", "IND-GEAR-220", 30, 5200),
        # Shubham Enterprise
        ("Shubham Enterprise", "Available WH - SHE", "ENGINE-15W40", 250, 520),
        ("Shubham Enterprise", "Available WH - SHE", "ENGINE-5W30", 100, 600),
        ("Shubham Enterprise", "Available WH - SHE", "2W-ENGINE-5W30", 120, 480),
        ("Shubham Enterprise", "Available WH - SHE", "TRK-ENGINE-20W50", 60, 1800),
        ("Shubham Enterprise", "Available WH - SHE", "FARM-HYDRAULIC-32", 40, 2000),
    ]
    for company_name, warehouse, item_code, qty, rate in stock_data:
        existing = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0
        if flt(existing) < qty:
            se = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Receipt",
                "company": company_name,
                "posting_date": today(),
                "items": [{
                    "item_code": item_code,
                    "t_warehouse": warehouse,
                    "qty": qty - existing,
                    "uom": "Nos",
                    "transfer_qty": qty - existing,
                    "basic_rate": rate,
                }]
            })
            se.insert(ignore_permissions=True)
            se.submit()
            print(f"  {se.name}: {qty - existing} x {item_code} @ {rate}/unit -> {warehouse}")
        else:
            print(f"  OK: {item_code} in {warehouse} = {existing}")
    frappe.db.commit()

    print("\n" + "=" * 60)
    print("MASTER DATA SETUP COMPLETE")
    print("=" * 60)
    _print_summary()


def _print_summary():
    print(f"\nCompanies:     {frappe.db.count('Company')}")
    print(f"Warehouses:    {frappe.db.count('Warehouse')}")
    print(f"Items:         {frappe.db.count('Item')}")
    print(f"Suppliers:     {frappe.db.count('Supplier')}")
    print(f"Customers:     {frappe.db.count('Customer')}")
    print(f"Stock Entries: {frappe.db.count('Stock Entry', {'docstatus': 1})}")
