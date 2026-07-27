export default {
  doctype: "Purchase Invoice",
  name: "procurement",
  label: "Procurement",
  icon: "cube-outline",
  color: "#10b981",
  list: {
    route: "/procurement",
    title: "Purchase Invoices",
    columns: [
      { label: "ID", fieldname: "name", type: "Link" },
      { label: "Supplier", fieldname: "supplier", type: "Data" },
      { label: "Date", fieldname: "posting_date", type: "Date" },
      { label: "Amount", fieldname: "grand_total", type: "Currency" },
      { label: "Status", fieldname: "status", type: "Badge" },
    ],
    filters: [
      { type: "select", label: "Status", fieldname: "status", options: ["", "Draft", "Submitted", "Paid", "Overdue"] },
      { type: "link", label: "Supplier", fieldname: "supplier", options: { doctype: "Supplier" } },
      { type: "date", label: "From", fieldname: "posting_date", operator: ">=" },
    ],
    searchField: "supplier",
    orderBy: "posting_date desc",
  },
}