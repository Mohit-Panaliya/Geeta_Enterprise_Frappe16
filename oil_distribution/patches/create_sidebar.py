import frappe
import json
from frappe.desk.doctype.workspace_sidebar.workspace_sidebar import WorkspaceSidebar


def execute():
    path = frappe.get_app_path("oil_distribution", "workspace_sidebar", "oil_distribution.json")
    with open(path) as f:
        data = json.load(f)

    if frappe.db.exists("Workspace Sidebar", "Oil Distribution"):
        frappe.delete_doc("Workspace Sidebar", "Oil Distribution", force=1)

    sidebar = frappe.new_doc("Workspace Sidebar")
    sidebar.update(
        {
            "title": data["title"],
            "app": data["app"],
            "module": data.get("module"),
            "header_icon": data.get("header_icon"),
            "standard": 1,
        }
    )
    for item_data in data["items"]:
        sidebar.append("items", {k: v for k, v in item_data.items() if k != "doctype"})

    sidebar.insert()
    frappe.db.commit()
    print(f"Created sidebar with {len(sidebar.items)} items")
