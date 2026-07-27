import { createRouter, createWebHistory } from "@ionic/vue-router"
import { generateRoutes } from "./generateRoutes"

const routes = [
  {
    path: "/",
    redirect: "/dashboards",
  },
  {
    path: "/dashboards",
    name: "Dashboard",
    component: () => import("@/views/Dashboards.vue"),
  },
  {
    path: "/command-center",
    name: "CommandCenter",
    component: () => import("@/views/CommandCenter.vue"),
  },
  {
    path: "/stock",
    name: "StockDashboard",
    component: () => import("@/views/StockDashboard.vue"),
  },
  // Custom views take priority over generated ListPage routes
  {
    path: "/ict",
    name: "ICT",
    component: () => import("@/views/ICT.vue"),
  },
  {
    path: "/reservations",
    name: "Reservations",
    component: () => import("@/views/Reservations.vue"),
  },
  {
    path: "/sales",
    name: "Sales",
    component: () => import("@/views/Sales.vue"),
  },
  {
    path: "/procurement",
    name: "Procurement",
    component: () => import("@/views/Procurement.vue"),
  },
  ...generateRoutes(),
]

const router = createRouter({
  history: createWebHistory("/oil-ops"),
  routes,
})

export default router
