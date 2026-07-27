import { io } from "socket.io-client"

let socket = null

export function getSocket() {
  if (socket) return socket
  const host = window.location.host
  socket = io(`${window.location.protocol}//${host}`, {
    withCredentials: true,
    transports: ["websocket", "polling"],
  })
  return socket
}

export function subscribeToDocType(doctype, callback) {
  const s = getSocket()
  s.emit("doctype_subscribe", doctype)
  s.on("list_update", (data) => {
    if (data.doctype === doctype) callback(data)
  })
  return () => {
    s.off("list_update")
    s.emit("doctype_unsubscribe", doctype)
  }
}
