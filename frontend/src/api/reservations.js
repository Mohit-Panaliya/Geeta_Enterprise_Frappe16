import { frappeRequest } from "frappe-ui"

export function getReservationKpis(company = "All", item = "") {
  return frappeRequest({
    url: "oil_distribution.api.oil_ops.get_reservation_kpis",
    params: { company, item },
  })
}

export function getReservedByCompany() {
  return frappeRequest({
    url: "oil_distribution.api.oil_ops.get_reserved_by_company",
  })
}

export function getActiveReservations(limit = 30, company = "All") {
  return frappeRequest({
    url: "oil_distribution.api.oil_ops.get_active_reservations",
    params: { limit, company },
  })
}

export function createStockReservation(payload) {
  return frappeRequest({
    url: "oil_distribution.api.oil_ops.create_stock_reservation",
    params: payload,
  })
}

export function getCompanyWarehouses(company) {
  return frappeRequest({
    url: "oil_distribution.api.oil_ops.get_company_warehouses",
    params: { company },
  })
}

export function getItemStock(itemCode, warehouse) {
  return frappeRequest({
    url: "oil_distribution.api.oil_ops.get_item_stock",
    params: { item_code: itemCode, warehouse },
  })
}

export function getItemStockByCompany(itemCode, company) {
  return frappeRequest({
    url: "oil_distribution.api.oil_ops.get_item_stock_by_company",
    params: { item_code: itemCode, company },
  })
}

export function unreserveStockReservations(names) {
  return frappeRequest({
    url: "oil_distribution.api.oil_ops.unreserve_stock_reservations",
    params: { names },
  })
}
