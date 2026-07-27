import { getObjectList } from "@/objects"

export function generateRoutes() {
  const routes = []

  getObjectList().forEach((obj) => {
    if (!obj.list) return

    // List route
    routes.push({
      path: obj.list.route,
      name: `${obj.name}List`,
      meta: { object: obj.name, title: obj.list.title },
      component: () => import("@/pages/ListPage.vue"),
    })

    // Detail route
    if (obj.detail) {
      routes.push({
        path: obj.detail.route,
        name: `${obj.name}Detail`,
        meta: { object: obj.name, title: obj.label },
        component: () => import("@/pages/DetailPage.vue"),
      })
    }
  })

  return routes
}
