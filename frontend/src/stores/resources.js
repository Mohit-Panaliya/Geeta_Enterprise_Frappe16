import { defineStore } from "pinia"
import { ref, shallowRef } from "vue"
import { createResource, createListResource } from "frappe-ui"

export const useResourceStore = defineStore("resources", () => {
  const cache = shallowRef({})

  function getResource(key, options) {
    if (cache.value[key]) return cache.value[key]
    if (options && options.list) {
      cache.value[key] = createListResource({ ...options, cache: key })
    } else {
      cache.value[key] = createResource({ ...options, cache: key })
    }
    return cache.value[key]
  }

  function invalidate(key) {
    if (cache.value[key]) {
      cache.value[key].reload()
    }
  }

  function clearAll() {
    Object.values(cache.value).forEach((r) => { if (r.destroy) r.destroy() })
    cache.value = {}
  }

  return { cache, getResource, invalidate, clearAll }
})
