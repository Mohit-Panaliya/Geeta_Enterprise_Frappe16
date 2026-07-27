<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start"><ion-menu-button /></ion-buttons>
        <ion-title>{{ object?.list?.title || object?.label || 'List' }}</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content>
      <div class="page">
        <!-- Filters toggle + Quick Search -->
        <div class="flex items-center justify-between mb-3 gap-2 flex-wrap">
          <button class="btn btn-outline !text-xs !py-2 !px-4" @click="showFilters = !showFilters">
            <svg class="w-3.5 h-3.5 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            Filters
          </button>
          <div v-if="object?.list?.searchField" class="relative min-w-[180px] max-w-xs">
            <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input v-model="searchQuery" type="text"
              :placeholder="'Search ' + (typeof object?.list?.searchField === 'string' ? object?.list?.searchField : (object?.list?.searchField?.label || ''))"
              class="form-input !text-xs !py-2 !pl-8 w-full" @input="debouncedSearch" />
          </div>
        </div>

        <!-- Filters -->
        <div v-if="showFilters" class="flex items-center gap-3 mb-4 flex-wrap">
          <template v-for="f in object?.list?.filters" :key="f.fieldname">
            <div class="relative" :class="f.type === 'text' || f.type === 'link' ? 'min-w-[160px]' : ''">
              <input v-if="f.type === 'text' || f.type === 'link'" v-model="filterValues[f.fieldname]"
                :placeholder="f.label" class="form-input !text-xs !py-2"
                :class="f.type === 'text' ? '!w-40' : '!w-48'"
                @input="debouncedSearch" />
              <input v-else-if="f.type === 'date'" v-model="filterValues[f.fieldname]"
                type="date" :placeholder="f.label" class="form-input !text-xs !py-2 !w-40" @change="applyFilters" />
              <select v-else-if="f.type === 'select'" v-model="filterValues[f.fieldname]"
                class="form-input !text-xs !py-2 !w-auto" @change="applyFilters">
                <option v-for="o in f.options" :key="o" :value="o === '' ? '' : o === f.label ? '' : o">
                  {{ o || 'All ' + f.label }}
                </option>
              </select>
              <span v-if="filterValues[f.fieldname] && f.operator"
                class="absolute -top-2 -right-1 text-[10px] leading-none text-gray-400 bg-white px-0.5 z-10">{{ f.operator }}</span>
            </div>
          </template>
          <button class="btn btn-outline !text-xs !py-2 !px-4" @click="clearFilters">Clear</button>
        </div>

        <!-- Loading skeleton -->
        <div v-if="loading" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th v-for="col in skeletonColumns" :key="col" class="skeleton-head">&nbsp;</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in 4" :key="r">
                <td v-for="c in skeletonColumns" :key="c"><div class="skeleton-cell">&nbsp;</div></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty -->
        <div v-else-if="!rows?.length" class="text-center py-12 text-sm text-gray-400">No data found</div>

        <!-- Table -->
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th v-for="col in object?.list?.columns" :key="col.fieldname"
                  class="cursor-pointer select-none min-w-[100px]" @click="toggleSort(col.fieldname)">
                  <span class="inline-flex items-center gap-1">
                    {{ col.label }}
                    <span class="sort-indicator text-xs"
                      :class="sortField === col.fieldname ? 'text-gray-800 font-bold' : 'text-gray-300'">
                      {{ sortField === col.fieldname ? (sortDir === 'asc' ? '↑' : '↓') : '↑↓' }}
                    </span>
                  </span>
                </th>
                <th v-if="hasActions" class="text-center w-24">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.name"
                class="cursor-pointer" @click="goToDetail(row.name)">
                <td v-for="col in object?.list?.columns" :key="col.fieldname"
                  :style="col.width ? `min-width:${col.width}` : ''">
                  <span v-if="col.type === 'Badge'" class="badge" :class="'badge-' + (statusColor(row[col.fieldname]) || 'gray')">
                    {{ row[col.fieldname] }}
                  </span>
                  <span v-else-if="col.type === 'Currency'">{{ formatCurrency(row[col.fieldname]) }}</span>
                  <span v-else-if="col.type === 'Date'">{{ formatDate(row[col.fieldname]) }}</span>
                  <span v-else>{{ row[col.fieldname] }}</span>
                </td>
                <td v-if="hasActions" class="text-center whitespace-nowrap" @click.stop>
                  <template v-for="act in object?.list?.actions" :key="act.label || act.type">
                    <button v-if="act.action === 'delete' || act.type === 'delete'" class="btn btn-ghost !text-xs !py-1 !px-2 text-red-500"
                      @click="confirmDelete(row, act)">{{ act.label || 'Delete' }}</button>
                    <button v-else-if="act.action === 'edit' || act.type === 'edit'" class="btn btn-ghost !text-xs !py-1 !px-2"
                      @click="goToDetail(row.name)">{{ act.label || 'Edit' }}</button>
                    <button v-else class="btn btn-ghost !text-xs !py-1 !px-2"
                      @click="executeAction(row, act)">{{ act.label || 'Action' }}</button>
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="paginationInfo" class="text-center py-2 text-xs text-gray-500">
            {{ paginationInfo }}
          </div>
          <div v-if="hasMore" class="text-center py-3">
            <button class="btn btn-outline !text-xs !py-2 !px-6" @click="loadMore">Load More</button>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { IonPage, IonHeader, IonToolbar, IonButtons, IonMenuButton, IonTitle, IonContent } from "@ionic/vue"
import { call } from "frappe-ui"
import { getObject } from "@/objects"
import { subscribeToDocType } from "@/socket"

const route = useRoute()
const router = useRouter()

const objectName = route.meta?.object
const object = computed(() => getObject(objectName))

const rows = ref([])
const loading = ref(true)
const sortField = ref(object.value?.list?.orderBy?.split(" ")[0] || "name")
const sortDir = ref(object.value?.list?.orderBy?.includes("desc") ? "desc" : "asc")
const filterValues = ref({})
const hasMore = ref(false)
const showFilters = ref(true)
const searchQuery = ref("")
const totalCount = ref(0)
const pageStart = ref(0)
const pageLength = ref(50)
let unsubscribe = null

const hasActions = computed(() => object.value?.list?.actions?.length > 0)

const skeletonColumns = computed(() => {
  const cols = object.value?.list?.columns
  if (cols?.length) return cols.map(() => ({}))
  return Array(4).fill(null).map((_, i) => ({ fieldname: i }))
})

const paginationInfo = computed(() => {
  if (!rows.value.length || !totalCount.value) return ""
  const start = pageStart.value + 1
  const end = start + rows.value.length - 1
  return `Showing ${start}–${end} of ${totalCount.value}`
})

function buildFilters() {
  const filters = []
  if (searchQuery.value && object.value?.list?.searchField) {
    const sf = object.value.list.searchField
    const field = typeof sf === "string" ? sf : sf.fieldname
    filters.push([field, "like", "%" + searchQuery.value + "%"])
  }
  Object.entries(filterValues.value).forEach(([k, v]) => {
    if (v) {
      const fdef = object.value?.list?.filters?.find((f) => f.fieldname === k)
      if (fdef?.operator) {
        filters.push([k, fdef.operator, v])
      } else {
        filters.push([k, "=", v])
      }
    }
  })
  return filters
}

async function loadData() {
  loading.value = true
  pageStart.value = 0
  try {
    const doctype = object.value?.doctype
    const fields = ["name", ...(object.value?.list?.columns?.map((c) => c.fieldname) || [])]
    const filters = buildFilters()
    const orderBy = sortField.value + " " + sortDir.value
    console.log("[ListPage] fetching", doctype, { fields, filters, orderBy, pageLength: pageLength.value })
    const data = await call("frappe.client.get_list", {
      doctype,
      fields,
      filters,
      order_by: orderBy,
      limit_start: pageStart.value,
      limit_page_length: pageLength.value,
    })
    console.log("[ListPage] got", data?.length, "rows")
    rows.value = data || []
    hasMore.value = (data?.length || 0) >= pageLength.value
    totalCount.value = hasMore.value ? pageStart.value + (data?.length || 0) + 1 : pageStart.value + (data?.length || 0)
  } catch (e) {
    console.error("[ListPage] fetch error", e)
    rows.value = []
  }
  loading.value = false
}

async function loadMore() {
  if (!hasMore.value) return
  try {
    pageStart.value += pageLength.value
    const doctype = object.value?.doctype
    const fields = ["name", ...(object.value?.list?.columns?.map((c) => c.fieldname) || [])]
    const filters = buildFilters()
    const orderBy = sortField.value + " " + sortDir.value
    const data = await call("frappe.client.get_list", {
      doctype,
      fields,
      filters,
      order_by: orderBy,
      limit_start: pageStart.value,
      limit_page_length: pageLength.value,
    })
    rows.value = [...rows.value, ...(data || [])]
    hasMore.value = (data?.length || 0) >= pageLength.value
  } catch (e) {
    pageStart.value -= pageLength.value
    console.error("[ListPage] loadMore error", e)
  }
}

function toggleSort(field) {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === "asc" ? "desc" : "asc"
  } else {
    sortField.value = field
    sortDir.value = "asc"
  }
  loadData()
}

function applyFilters() { loadData() }

function clearFilters() {
  filterValues.value = {}
  searchQuery.value = ""
  loadData()
}

function goToDetail(name) {
  if (object.value?.detail) {
    router.push(object.value.detail.route.replace(":name", name))
  }
}

async function confirmDelete(row, action) {
  if (action.confirm) {
    const ok = window.confirm(`Delete ${row.name}?`)
    if (!ok) return
  }
  try {
    await call("frappe.client.delete", { doctype: object.value.doctype, name: row.name })
    loadData()
  } catch (e) {
    console.error("[ListPage] Delete failed", e)
  }
}

function executeAction(row, action) {
  if (typeof action.handler === "function") {
    action.handler(row)
  } else if (action.type === "edit") {
    goToDetail(row.name)
  }
}

function statusColor(status) {
  const map = { Submitted: "green", Paid: "green", Reserved: "amber", Released: "blue", Cancelled: "gray", Draft: "amber" }
  return map[status]
}

function formatCurrency(v) {
  const n = parseFloat(v) || 0
  return "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 0 })
}

function formatDate(v) {
  if (!v) return ""
  const d = new Date(v)
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })
}

let debounceTimer = null
function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(applyFilters, 300)
}

onMounted(() => {
  loadData()
  if (object.value?.doctype) {
    unsubscribe = subscribeToDocType(object.value.doctype, () => loadData())
  }
})

onUnmounted(() => {
  if (unsubscribe) unsubscribe()
})
</script>

<style scoped>
@keyframes shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: calc(400px + 100%) 0; }
}

.skeleton-head {
  height: 28px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 400px 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
}

.skeleton-cell {
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 400px 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
  margin: 4px 0;
}

.sort-indicator {
  font-variant-numeric: tabular-nums;
}
</style>
