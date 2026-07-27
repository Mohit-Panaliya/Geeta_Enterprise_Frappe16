export default {
  doctype: "Sales Invoice",
  name: "sales",
  label: "Sales",
  icon: "cart-outline",
  color: "#3b82f6",
  list: {
    route: "/sales",
    title: "Sales Invoices",
    columns: [
      { label: "ID", fieldname: "name", type: "Link" },
      { label: "Customer", fieldname: "customer", type: "Data" },
      { label: "Date", fieldname: "posting_date", type: "Date" },
      { label: "Amount", fieldname: "grand_total", type: "Currency" },
      { label: "Status", fieldname: "status", type: "Badge" },
    ],
    filters: [
      { type: "select", label: "Status", fieldname: "status", options: ["", "Draft", "Submitted", "Paid", "Overdue"] },
      { type: "link", label: "Customer", fieldname: "customer", options: { doctype: "Customer" } },
      { type: "date", label: "From", fieldname: "posting_date", operator: ">=" },
    ],
    searchField: "customer",
    orderBy: "posting_date desc",
  },
  detail: {
    route: "/sales/:name",
    tabs: [
      { label: "Items", component: "SalesItems" },
      { label: "Payments", component: "SalesPayments" },
    ],
  },
}