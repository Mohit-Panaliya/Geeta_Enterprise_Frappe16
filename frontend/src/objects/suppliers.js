export default {
  doctype: "Supplier",
  name: "suppliers",
  label: "Suppliers",
  icon: "business-outline",
  color: "#f43f5e",
  list: {
    route: "/suppliers",
    title: "Suppliers",
    columns: [
      { label: "Name", fieldname: "supplier_name", type: "Link" },
      { label: "Type", fieldname: "supplier_type", type: "Data" },
      { label: "Group", fieldname: "supplier_group", type: "Data" },
      { label: "Country", fieldname: "country", type: "Data" },
    ],
    filters: [
      { type: "select", label: "Type", fieldname: "supplier_type", options: ["", "Company", "Individual"] },
      { type: "text", label: "Search", fieldname: "supplier_name" },
    ],
    searchField: "supplier_name",
    orderBy: "supplier_name asc",
    hasMoreFilters: true,
    actions: [
      { label: "Edit", icon: "create-outline", action: "edit" },
      { label: "Delete", icon: "trash-outline", action: "delete", confirm: true },
    ],
  },
  detail: {
    route: "/suppliers/:name",
    fields: [
      { label: "Supplier Name", fieldname: "supplier_name", type: "Data", required: true },
      { label: "Supplier Type", fieldname: "supplier_type", type: "Select", required: true, options: ["Company", "Individual"] },
      { label: "Supplier Group", fieldname: "supplier_group", type: "Data" },
      { label: "Country", fieldname: "country", type: "Data" },
      { label: "Default Currency", fieldname: "default_currency", type: "Data" },
      { label: "Tax ID", fieldname: "tax_id", type: "Data" },
      { label: "Is Internal Supplier", fieldname: "is_internal_supplier", type: "Check" },
      { label: "Disabled", fieldname: "disabled", type: "Check" },
    ],
  },
}