import frappe

items = frappe.get_all("Item", fields=["name", "item_name"])
for i in items:
    doc = frappe.get_doc("Item", i.name)
    has_litre = any(u.uom == "Litre" for u in doc.uoms)
    if has_litre:
        continue
    
    # Add Litre conversion based on item type
    if i.name.startswith("FARM-") or i.name.startswith("IND-") or i.name.startswith("TRK-"):
        factor = 5.0
    elif i.name.startswith("4W-"):
        factor = 1.0  # already has it but just in case
    elif i.name.startswith("2W-"):
        factor = 2.5  # already has it
    else:
        factor = 1.0
    
    doc.append("uoms", {"uom": "Litre", "conversion_factor": factor})
    doc.flags.ignore_permissions = True
    doc.flags.ignore_validate = True
    doc.save(ignore_permissions=True)
    print(f"Added Litre (factor={factor}) to {i.name}")
