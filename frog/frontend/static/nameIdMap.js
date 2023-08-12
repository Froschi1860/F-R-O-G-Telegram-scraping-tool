import { apiGet } from "./api.js"
import { activateBtn, deactivateBtn } from "./util.js"

const handleIdLookup = async e => {
  let resultField = document.getElementById("channel-id-result")
  let channelRef = document.getElementById("channel-ref").value.trim()
  if (!channelRef) {
    resultField.innerHTML = "<p>Enter a reference to start</p>"
    return
  }
  activateBtn("channel-id-lookup", handleIdLookup, "Search")
  deactivateBtn("channel-id-lookup", "Searching...")
  let res = await apiGet(`/name-id-map/by-reference?channel_ref=${channelRef}`)
  activateBtn("channel-id-lookup", handleIdLookup, "Search")
  if (res.status === 200) return resultField.innerHTML = `<p>The ID is: <input value="${res[channelRef]}" readonly></p>`
  document.getElementById("channel-ref").value = ""
  if (res.status === 404) return resultField.innerHTML = "<p>Channel not found</p>"
  if (res.status == 400) return resultField.innerHTML = "<p>Bad request</p>"
  if (res.status == 409) return resultField.innerHTML = "<p>Telethon client is busy or no client is available. Retry when scraping process is done.</p>"
  resultField.innerHTML = "<p>An error occured on lookup.</p>"
}

const handleRefLookup = async e => {
  let resultField = document.getElementById("ref-list")
  let channelId = document.getElementById("channel-id").value
  if (!channelId) return resultField.innerHTML = "<li>Enter an ID to start</li>"
  if (isNaN(channelId) || Number(channelId) < 1) return resultField.innerHTML = "<li>ID must be a positive integer.</li>"
  deactivateBtn("channel-ref-lookup", "Searching...")
  let res = await apiGet(`/name-id-map/by-id?channel_id=${channelId}`)
  activateBtn("channel-ref-lookup", handleRefLookup, "Search")
  if (res.status === 200) {
    resultField.innerHTML = ""
    if (res[channelId].length === 0) return resultField.innerHTML = "<li>No results found.</li>"
    res[channelId].forEach(element => {
      resultField.innerHTML += `<li><input value="${element}" readonly></li>`
    })
    return
  }
  document.getElementById("channel-ref").value = ""
  if (res.status === 404) return resultField.innerHTML = "<li>Channel not found</li>"
  if (res.status === 400) return resultField.innerHTML = "<li>Bad request</li>"
  if (res.status === 409) return resultField.innerHTML = "<li>Telethon client is busy or no client is available. Retry when scraping process is done.</li>"
  resultField.innerHTML = "<li>An error occured on lookup.</li>"
}

activateBtn("channel-id-lookup", handleIdLookup, "Search")
activateBtn("channel-ref-lookup", handleRefLookup, "Search")