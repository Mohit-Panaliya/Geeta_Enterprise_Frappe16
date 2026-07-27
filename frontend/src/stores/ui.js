import { defineStore } from "pinia"
import { ref, watch } from "vue"

export const useUiStore = defineStore("ui", () => {
  const sidebarCollapsed = ref(localStorage.getItem("geo-sidebar-collapsed") === "true")
  const darkMode = ref(localStorage.getItem("geo-dark-mode") === "true")
  const activeCompany = ref(localStorage.getItem("geo-company") || "All")
  const activeItem = ref(localStorage.getItem("geo-item") || "All")

  watch(sidebarCollapsed, (v) => localStorage.setItem("geo-sidebar-collapsed", v))
  watch(darkMode, (v) => localStorage.setItem("geo-dark-mode", v))
  watch(activeCompany, (v) => localStorage.setItem("geo-company", v))
  watch(activeItem, (v) => localStorage.setItem("geo-item", v))

  function toggleSidebar() { sidebarCollapsed.value = !sidebarCollapsed.value }

  return { sidebarCollapsed, darkMode, activeCompany, activeItem, toggleSidebar }
})
