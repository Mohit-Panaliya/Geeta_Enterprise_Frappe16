<template>
  <ion-app>
    <ion-split-pane :content-id="'main-content'" :when="true">
      <ion-menu :content-id="'main-content'" side="start" :class="{ collapsed: uiStore.sidebarCollapsed }">
        <ion-header class="ion-no-border">
          <ion-toolbar>
            <div class="flex items-center gap-2.5" :class="uiStore.sidebarCollapsed ? 'justify-center' : ''">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-sm flex-shrink-0">
                <ion-icon :icon="waterOutline" class="text-white text-lg" />
              </div>
              <div v-if="!uiStore.sidebarCollapsed">
                <div class="text-sm font-bold text-gray-900">GEOperations</div>
                <div class="text-[10px] font-medium text-gray-400 tracking-wide">DASHBOARD</div>
              </div>
            </div>
          </ion-toolbar>
        </ion-header>
        <div v-if="!uiStore.sidebarCollapsed" class="user-section">
          <div class="flex items-center gap-3 px-4 py-3 border-b border-gray-100">
            <div v-if="user.user_image" class="w-9 h-9 rounded-full overflow-hidden flex-shrink-0">
              <img :src="user.user_image" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              {{ userInitial }}
            </div>
            <div class="min-w-0">
              <div class="text-sm font-semibold text-gray-800 truncate">{{ user.full_name || user.name }}</div>
              <div class="text-[11px] text-gray-400 truncate">{{ user.name }}</div>
            </div>
          </div>
        </div>
        <ion-content>
          <div v-if="!uiStore.sidebarCollapsed" class="px-3 pt-2 pb-1">
            <div class="relative">
              <ion-icon :icon="searchOutline" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm pointer-events-none" />
              <input v-model="searchQuery" type="search" placeholder="Search..." class="sidebar-search-input" />
            </div>
          </div>
          <ion-list>
            <div v-for="group in filteredGroups" :key="group.label">
              <div class="nav-group-header" @click="toggleGroup(group.label)">
                <span class="text-[10px] font-bold tracking-widest text-gray-400 uppercase">{{ group.label }}</span>
                <ion-icon :icon="group.expanded ? chevronDownOutline : chevronForwardOutline" class="text-gray-300 text-sm" />
              </div>
              <div class="nav-group-items" :class="{ expanded: group.expanded }">
                <ion-item v-for="item in group.items" :key="item.route"
                  :router-link="item.route" router-direction="root"
                  :class="{ selected: isActive(item.route) }">
                  <div class="icon-wrapper" :class="{ active: isActive(item.route) }" :style="iconWrapperStyle(item)">
                    <ion-icon :icon="item.icon" :style="isActive(item.route) && item.color ? { color: item.color } : {}" />
                  </div>
                  <ion-label v-if="!uiStore.sidebarCollapsed">{{ item.label }}</ion-label>
                </ion-item>
              </div>
            </div>
          </ion-list>
          <div class="px-3 mt-4">
            <button class="btn btn-outline !text-xs !py-2 w-full flex items-center justify-center gap-2" @click="uiStore.toggleSidebar()">
              <ion-icon :icon="uiStore.sidebarCollapsed ? arrowForwardOutline : arrowBackOutline" class="text-sm" />
              <span v-if="!uiStore.sidebarCollapsed">Collapse</span>
            </button>
          </div>
        </ion-content>
      </ion-menu>
      <ion-router-outlet id="main-content" />
    </ion-split-pane>
  </ion-app>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { IonApp, IonSplitPane, IonMenu, IonHeader, IonToolbar, IonContent, IonList, IonItem, IonLabel, IonIcon, IonRouterOutlet } from "@ionic/vue"
import { useUiStore } from "@/stores/ui"
import { frappeRequest } from "frappe-ui"
import { objects } from "@/objects"
import {
  waterOutline, gridOutline, pulseOutline, analyticsOutline,
  cartOutline, desktopOutline, serverOutline,
  peopleOutline, businessOutline, cubeOutline,
  chevronDownOutline, chevronForwardOutline,
  arrowForwardOutline, arrowBackOutline,
  searchOutline
} from "ionicons/icons"

const $route = useRoute()
const uiStore = useUiStore()
const searchQuery = ref("")

const user = ref({ name: "Administrator", full_name: "", user_image: "" })

onMounted(async () => {
  try {
    const sessionUser = (typeof frappe !== "undefined" && frappe.session?.user) || "Administrator"
    const res = await frappeRequest({
      url: "frappe.client.get",
      params: {
        doctype: "User",
        name: sessionUser,
        fields: JSON.stringify(["name", "full_name", "user_image"]),
      },
    })
    if (res) user.value = res
  } catch (e) {
    // silent
  }
})

const userInitial = computed(() => {
  const name = user.value.full_name || user.value.name
  return name ? name.charAt(0).toUpperCase() : "?"
})

function buildMasterDataItems() {
  return ["customers", "suppliers", "items"]
    .filter((name) => objects[name])
    .map((name) => {
      const obj = objects[name]
      return {
        route: obj.list?.route || `/${obj.name}`,
        label: obj.label,
        icon: obj.icon,
        color: obj.color,
      }
    })
}

const navGroups = reactive([
  {
    label: "Dashboards",
    expanded: true,
    items: [
      { route: "/dashboards", label: "Overview", icon: gridOutline },
      { route: "/command-center", label: "Command Center", icon: pulseOutline },
      { route: "/stock", label: "Stock Dashboard", icon: analyticsOutline },
    ],
  },
  {
    label: "Transactions",
    expanded: true,
    items: [
      { route: "/sales", label: "Sales", icon: desktopOutline },
      { route: "/procurement", label: "Procurement", icon: cartOutline },
      { route: "/ict", label: "ICT", icon: serverOutline },
      { route: "/reservations", label: "Reservations", icon: waterOutline },
    ],
  },
  {
    label: "Master Data",
    expanded: true,
    items: buildMasterDataItems(),
  },
])

const filteredGroups = computed(() => {
  const q = searchQuery.value?.trim().toLowerCase()
  if (!q) return navGroups
  return navGroups
    .map((g) => ({
      ...g,
      expanded: true,
      items: g.items.filter((item) => item.label.toLowerCase().includes(q)),
    }))
    .filter((g) => g.items.length > 0)
})

function toggleGroup(label) {
  if (searchQuery.value?.trim()) return
  const g = navGroups.find((n) => n.label === label)
  if (g) g.expanded = !g.expanded
}

function isActive(route) {
  return $route.path === route || $route.path.startsWith(route + "/")
}

function iconWrapperStyle(item) {
  if (!isActive(item.route)) return {}
  return { backgroundColor: (item.color || "#6366f1") + "1a" }
}
</script>

<style scoped>
.user-section {
  border-bottom: 1px solid #f3f4f6;
}

.sidebar-search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.25rem;
  font-size: 0.875rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.sidebar-search-input:focus {
  border-color: #a5b4fc;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.sidebar-search-input::placeholder {
  color: #9ca3af;
}

.nav-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem 0.5rem;
  cursor: pointer;
  transition: opacity 0.15s;
}

.nav-group-header:hover {
  opacity: 0.75;
}

.nav-group-items {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.nav-group-items.expanded {
  max-height: 500px;
}

ion-item {
  --border-style: none;
  --padding-start: 12px;
  --padding-end: 12px;
  --min-height: 40px;
  --background-hover: #f3f4f6;
  border-radius: 8px;
  margin: 2px 8px;
  cursor: pointer;
  --transition: background-color 0.15s;
}

ion-item.selected {
  --background: rgba(99, 102, 241, 0.12);
  font-weight: 600;
}

ion-item.selected ion-label {
  color: #4338ca;
  font-weight: 600;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  flex-shrink: 0;
  margin-right: 12px;
  transition: background-color 0.15s;
}

.icon-wrapper ion-icon {
  font-size: 18px;
  color: #6b7280;
  transition: color 0.15s;
}

.icon-wrapper.active {
  background-color: rgba(99, 102, 241, 0.15);
}

.icon-wrapper.active ion-icon {
  color: #6366f1;
}

ion-item:hover {
  --background: #f9fafb;
}
</style>
