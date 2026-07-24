import frappe

def check_uom():
    items = frappe.get_all("Item", fields=["name", "item_name"])
    for i in items:
        doc = frappe.get_doc("Item", i.name)
        has_litre = any(u.uom == "Litre" for u in doc.uoms)
        lf = ""
        for u in doc.uoms:
            if u.uom == "Litre":
                lf = str(u.conversion_factor)
        status = f"HAS Litre (factor={lf})" if has_litre else "MISSING Litre"
        print(f"{i.name:30s} {status}")

def add_uom():
    items = frappe.get_all("Item", fields=["name", "item_name"])
    for i in items:
        doc = frappe.get_doc("Item", i.name)
        has_litre = any(u.uom == "Litre" for u in doc.uoms)
        if has_litre:
            continue
        if i.name.startswith("FARM-") or i.name.startswith("IND-") or i.name.startswith("TRK-"):
            factor = 5.0
        else:
            factor = 1.0
        doc.append("uoms", {"uom": "Litre", "conversion_factor": factor})
        doc.flags.ignore_permissions = True
        doc.flags.ignore_validate = True
        doc.save(ignore_permissions=True)
        print(f"  Added Litre (factor={factor}) to {i.name}")
