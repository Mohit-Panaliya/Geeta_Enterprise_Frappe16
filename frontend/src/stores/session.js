import { defineStore } from "pinia"
import { ref } from "vue"
import { frappeRequest } from "frappe-ui"

export const useSessionStore = defineStore("session", () => {
  const user = ref(null)
  const loggedIn = ref(false)
  const loading = ref(true)

  async init() {
    try {
      const d = await frappeRequest({ url: "/api/method/frappe.auth.get_logged_user" })
      user.value = d.message
      loggedIn.value = true
    } catch {
      user.value = null
      loggedIn.value = false
    }
    loading.value = false
  }

  return { user, loggedIn, loading, init }
})
