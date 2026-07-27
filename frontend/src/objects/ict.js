export default {
  doctype: "Inter Company Transfer",
  name: "ict",
  label: "ICT",
  icon: "server-outline",
  color: "#7c3aed",
  list: {
    route: "/ict",
    title: "Inter Company Transfers",
    columns: [
      { label: "ID", fieldname: "name", type: "Link" },
      { label: "From", fieldname: "company", type: "Data" },
      { label: "To", fieldname: "to_company", type: "Data" },
      { label: "Qty (Nos)", fieldname: "total_nos", type: "Float" },
      { label: "Qty (L)", fieldname: "total_litres", type: "Float" },
      { label: "Value", fieldname: "grand_total", type: "Currency" },
      { label: "Status", fieldname: "status", type: "Badge" },
    ],
    filters: [
      { type: "select", label: "Status", fieldname: "status", options: ["", "Draft", "Submitted", "Cancelled"] },
      { type: "link", label: "Company", fieldname: "company", options: { doctype: "Company" } },
      { type: "link", label: "To Company", fieldname: "to_company", options: { doctype: "Company" } },
      { type: "date", label: "From", fieldname: "posting_date", operator: ">=" },
    ],
    searchField: "name",
    orderBy: "posting_date desc",
  },
  detail: {
    route: "/ict/:name",
    tabs: [
      { label: "Items", component: "ICTItems" },
      { label: "Dashboard", component: "ICTDashboard" },
    ],
  },
}