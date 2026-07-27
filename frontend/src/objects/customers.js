export default {
  doctype: "Customer",
  name: "customers",
  label: "Customers",
  icon: "people-outline",
  color: "#6366f1",
  list: {
    route: "/customers",
    title: "Customers",
    columns: [
      { label: "Name", fieldname: "customer_name", type: "Link" },
      { label: "Type", fieldname: "customer_type", type: "Data" },
      { label: "Group", fieldname: "customer_group", type: "Data" },
      { label: "Territory", fieldname: "territory", type: "Data" },
    ],
    filters: [
      { type: "select", label: "Type", fieldname: "customer_type", options: ["", "Individual", "Company"] },
      { type: "text", label: "Search", fieldname: "customer_name" },
    ],
    searchField: "customer_name",
    orderBy: "customer_name asc",
    hasMoreFilters: true,
    actions: [
      { label: "Edit", icon: "create-outline", action: "edit" },
      { label: "Delete", icon: "trash-outline", action: "delete", confirm: true },
    ],
  },
  detail: {
    route: "/customers/:name",
    fields: [
      { label: "Customer Name", fieldname: "customer_name", type: "Data", required: true },
      { label: "Customer Type", fieldname: "customer_type", type: "Select", required: true, options: ["Individual", "Company"] },
      { label: "Customer Group", fieldname: "customer_group", type: "Data" },
      { label: "Territory", fieldname: "territory", type: "Data" },
      { label: "Default Currency", fieldname: "default_currency", type: "Data" },
      { label: "Tax ID", fieldname: "tax_id", type: "Data" },
      { label: "Is Internal Customer", fieldname: "is_internal_customer", type: "Check" },
      { label: "Disabled", fieldname: "disabled", type: "Check" },
    ],
  },
}