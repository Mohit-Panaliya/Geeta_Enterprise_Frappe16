export default {
  doctype: "Stock Reservation",
  name: "reservations",
  label: "Reservations",
  icon: "water-outline",
  color: "#0891b2",
  list: {
    route: "/reservations",
    title: "Stock Reservations",
    columns: [
      { label: "ID", fieldname: "name", type: "Link" },
      { label: "Company", fieldname: "company", type: "Data" },
      { label: "Item", fieldname: "item_code", type: "Data" },
      { label: "Qty", fieldname: "reserved_qty", type: "Float" },
      { label: "Status", fieldname: "status", type: "Badge" },
    ],
    filters: [
      { type: "select", label: "Status", fieldname: "status", options: ["", "Reserved", "Released", "Cancelled"] },
      { type: "link", label: "Company", fieldname: "company", options: { doctype: "Company" } },
    ],
    searchField: "item_code",
    orderBy: "reservation_date desc",
  },
}