<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start"><ion-back-button default-href="/dashboards" /></ion-buttons>
        <ion-title>{{ doc?.name || object?.label || 'Detail' }}</ion-title>
        <ion-buttons slot="end">
          <button v-if="!editing" class="btn btn-outline !text-xs !py-1.5 !px-3" @click="enterEdit">Edit</button>
          <template v-if="editing">
            <button class="btn btn-primary !text-xs !py-1.5 !px-3" @click="saveDoc">Save</button>
            <button class="btn btn-outline !text-xs !py-1.5 !px-3 ml-2" @click="cancelEdit">Cancel</button>
          </template>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>
    <ion-content>
      <div class="page">
        <div v-if="loading" class="text-center py-12 text-sm text-gray-400">Loading...</div>
        <div v-else-if="!doc" class="text-center py-12 text-sm text-gray-400">Not found</div>
        <template v-else>
          <div class="card-white mb-4">
            <div class="flex items-center justify-between mb-4">
              <div>
                <div class="text-lg font-extrabold text-gray-900">{{ doc.name }}</div>
                <div class="text-xs text-gray-400 mt-1">{{ object?.label }}</div>
              </div>
              <div class="flex items-center gap-3">
                <span v-if="doc.status" class="badge" :class="'badge-' + statusColor(doc.status)">{{ doc.status }}</span>
                <button v-if="!editing" class="text-xs font-semibold text-red-500 hover:text-red-700 transition-colors" @click="confirmDelete">Delete</button>
              </div>
            </div>

            <div v-if="message" class="mb-3 px-3 py-2 rounded-lg text-xs font-semibold" :class="messageType === 'error' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'">{{ message }}</div>

            <div v-if="!editing" class="grid grid-cols-2 gap-4 text-sm">
              <div v-for="col in fields" :key="col.fieldname">
                <div class="text-xs font-semibold text-gray-400 uppercase tracking-wide">{{ col.label }}</div>
                <div class="font-semibold text-gray-800 mt-0.5">
                  <span v-if="col.type === 'Currency'">{{ formatCurrency(doc[col.fieldname]) }}</span>
                  <span v-else-if="col.type === 'Date'">{{ formatDate(doc[col.fieldname]) }}</span>
                  <span v-else-if="col.type === 'Check'">{{ doc[col.fieldname] ? 'Yes' : 'No' }}</span>
                  <span v-else>{{ doc[col.fieldname] }}</span>
                </div>
              </div>
            </div>

            <div v-else class="grid grid-cols-2 gap-4">
              <div v-for="field in fields" :key="field.fieldname" class="form-group">
                <label class="form-label">{{ field.label }}</label>
                <input
                  v-if="field.type === 'Data' || field.type === 'Link' || !field.type"
                  v-model="formData[field.fieldname]"
                  class="form-input"
                />
                <select
                  v-else-if="field.type === 'Select'"
                  v-model="formData[field.fieldname]"
                  class="form-input"
                >
                  <option value="">Select...</option>
                  <option v-for="opt in (field.options || [])" :key="opt" :value="opt">{{ opt }}</option>
                </select>
                <input
                  v-else-if="field.type === 'Currency' || field.type === 'Float'"
                  v-model.number="formData[field.fieldname]"
                  type="number" step="0.01"
                  class="form-input"
                />
                <input
                  v-else-if="field.type === 'Int'"
                  v-model.number="formData[field.fieldname]"
                  type="number" step="1"
                  class="form-input"
                />
                <input
                  v-else-if="field.type === 'Date'"
                  v-model="formData[field.fieldname]"
                  type="date"
                  class="form-input"
                />
                <textarea
                  v-else-if="field.type === 'Text'"
                  v-model="formData[field.fieldname]"
                  class="form-input" rows="3"
                ></textarea>
                <label v-else-if="field.type === 'Check'" class="flex items-center gap-2 cursor-pointer pt-1">
                  <input v-model="formData[field.fieldname]" type="checkbox" class="w-4 h-4 rounded border-gray-300 text-blue-600" />
                  <span class="text-sm text-gray-700">{{ formData[field.fieldname] ? 'Yes' : 'No' }}</span>
                </label>
                <input v-else v-model="formData[field.fieldname]" class="form-input" />
              </div>
            </div>
          </div>

          <div v-if="object?.detail?.tabs?.length" class="card-white">
            <div class="flex gap-2 border-b border-gray-100 pb-3 mb-4">
              <button v-for="tab in object.detail.tabs" :key="tab.label"
                class="text-xs font-bold px-4 py-2 rounded-lg transition-colors"
                :class="activeTab === tab.label ? 'bg-blue-50 text-blue-600' : 'text-gray-400 hover:text-gray-600'"
                @click="activeTab = tab.label">{{ tab.label }}</button>
            </div>
            <component v-if="tabComponent" :is="tabComponent" :doc="doc" />
            <div v-else class="text-sm text-gray-500 text-center py-8">
              {{ activeTab }} content — component not found
            </div>
          </div>
        </template>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { IonPage, IonHeader, IonToolbar, IonButtons, IonBackButton, IonTitle, IonContent } from "@ionic/vue"
import { call } from "frappe-ui"
import { getObject } from "@/objects"

const route = useRoute()
const router = useRouter()
const objectName = route.meta?.object
const object = computed(() => getObject(objectName))

const doc = ref(null)
const loading = ref(true)
const editing = ref(false)
const formData = ref({})
const message = ref("")
const messageType = ref("success")
const activeTab = ref("")
const tabComponent = ref(null)

const fields = computed(() => object.value?.detail?.fields || object.value?.list?.columns || [])

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

function enterEdit() {
  formData.value = { ...doc.value }
  editing.value = true
  message.value = ""
}

function cancelEdit() {
  editing.value = false
  formData.value = {}
  message.value = ""
}

async function saveDoc() {
  message.value = ""
  try {
    const changed = fields.value.filter(f => formData.value[f.fieldname] !== doc.value[f.fieldname])
    if (changed.length === 0) {
      editing.value = false
      return
    }
    for (const f of changed) {
      await call("frappe.client.set_value", {
        doctype: doc.value.doctype,
        name: doc.value.name,
        fieldname: f.fieldname,
        value: formData.value[f.fieldname]
      })
    }
    const fresh = await call("frappe.client.get", {
      doctype: object.value.doctype,
      name: doc.value.name
    })
    doc.value = fresh
    editing.value = false
    message.value = "Saved successfully"
    messageType.value = "success"
    setTimeout(() => { message.value = "" }, 3000)
  } catch (e) {
    message.value = e.messages?.[0] || e.message || "Save failed"
    messageType.value = "error"
  }
}

async function confirmDelete() {
  if (!window.confirm(`Delete ${doc.value.name}? This action cannot be undone.`)) return
  try {
    await call("frappe.client.delete", {
      doctype: doc.value.doctype,
      name: doc.value.name
    })
    const listRoute = object.value?.list?.route || object.value?.detail?.route?.replace(/\/:name.*$/, "") || "/dashboards"
    router.push(listRoute)
  } catch (e) {
    message.value = e.messages?.[0] || e.message || "Delete failed"
    messageType.value = "error"
  }
}

watch(activeTab, async (label) => {
  const tab = object.value?.detail?.tabs?.find(t => t.label === label)
  if (!tab?.component) { tabComponent.value = null; return }
  const compName = tab.component
  const patterns = [
    () => import(`@/views/${objectName}/${compName}.vue`),
    () => import(`@/components/${compName}.vue`),
    () => import(`@/views/${compName}.vue`),
  ]
  for (const p of patterns) {
    try {
      const mod = await p()
      tabComponent.value = mod.default
      return
    } catch {}
  }
  tabComponent.value = null
})

onMounted(async () => {
  const name = route.params.name
  if (!name || !object.value) { loading.value = false; return }
  try {
    doc.value = await call("frappe.client.get", {
      doctype: object.value.doctype,
      name
    })
    if (object.value?.detail?.tabs?.length) {
      activeTab.value = object.value.detail.tabs[0].label
    }
  } catch (e) {
    console.error("[DetailPage] fetch error", e)
  }
  loading.value = false
})
</script>
