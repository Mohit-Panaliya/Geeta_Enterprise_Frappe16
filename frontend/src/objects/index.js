import sales from "./sales"
import procurement from "./procurement"
import ict from "./ict"
import reservations from "./reservations"
import items from "./items"
import customers from "./customers"
import suppliers from "./suppliers"

export const objects = {
  sales, procurement, ict, reservations,
  items, customers, suppliers,
}

export function getObject(name) {
  return objects[name]
}

export function getObjectList() {
  return Object.values(objects)
}
