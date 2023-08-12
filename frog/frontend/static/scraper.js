import { hideElement, displayElement, activateBtn, deactivateBtn } from "./util.js"
import { apiDelete, apiGet, apiPost, apiPut, getMetaData } from "./api.js"

let scrapeMultiRefs = []

const updateRefList = () => {
  const refList = document.getElementById("scrape-multi-refs")
  if (scrapeMultiRefs.length == 0) return refList.innerHTML = "<li>Enter references to start</li>"
  refList.innerHTML = ""
  scrapeMultiRefs.forEach(ref => {
    refList.innerHTML += `
    <li ref="${ref}"><button class="remove-ref" ref="${ref}">Remove</button>${ref}</li>`
  })
  let btns = Array.from(document.getElementsByClassName("remove-ref"))
  btns.forEach(btn => btn.addEventListener("click", removeFromRefList))
}

const removeFromRefList = e => {
  let idx = scrapeMultiRefs.indexOf(e.target.getAttribute("ref"))
  if (idx !== -1) scrapeMultiRefs.splice(idx, 1)
  updateRefList()
}

const addToRefList = ref => {
  if (ref === "" || scrapeMultiRefs.includes(ref)) return
  scrapeMultiRefs.push(ref)
  updateRefList()
}

const handleAddToRefBtnClick = e => {
  let inputField = document.getElementById("add-ref")
  let ref = inputField.value
  inputField.value = ""
  addToRefList(ref)
}

const handleRefFileUpload = async e => {
  let fileList = document.getElementById("channel-ref-files").files
  for (let file of fileList) {
    if (file.name.endsWith(".txt") || file.name.endsWith(".csv")) {
      let fileContent = await file.text()
      fileContent = fileContent.replaceAll(",", " ")
      fileContent = fileContent.replaceAll("\r\n", " ")
      fileContent.trim().split(/\s+/).forEach(ref => addToRefList(ref))
      document.getElementById("channel-ref-files").value = ""
    }
  }
}

const handleGetMetaBtnClick = async e => {
  let metaField = document.getElementById("channel-meta")
  let channelRef = document.getElementById("inp-channel-ref").value
  hideElement("cfg-and-start")
  metaField.textContent = ""
  metaField.innerHTML = ""
  if (channelRef === "") {
    metaField.textContent = "Please enter a channel reference."
    return
  }
  if (!isNaN(channelRef)) {
    metaField.textContent = "Channel reference cannot be a number."
    return
  }
  deactivateBtn("btn-get-channel-meta-by-ref", "Searching for metadata...")
  let url = `/scraper/single-channel-setup?channel_ref=${channelRef}`
  if (await getMetaData(url)) displayElement("cfg-and-start")
  metaField.innerHTML += `
    <p>Looked for reference: <input id="channel-ref-single" value="${channelRef}" readonly></p>`
  activateBtn("btn-get-channel-meta-by-ref", handleGetMetaBtnClick, "Get metadata")
}

const handleScraperStartMulti = async e => {
  let resField = document.getElementById("scraper-res-multi")
  if (scrapeMultiRefs.length === 0) return resField.innerHTML = "Enter references to start"
  resField.innerHTML = ""
  let body = { "refs": scrapeMultiRefs }
  let res
  if (e.target.id === "btn-start-scraper-multi") {
    deactivateBtn("btn-start-scraper-multi", "Scraper running...")
    res = await apiPost("/scraper/scrape-channels", body)
    activateBtn("btn-start-scraper-multi", handleScraperStartMulti, "Start new scraper job")
    if (res.status === 404) {
      return resField.innerHTML = "Error on scraper start: No clients available."
    }
  }
  if (e.target.id === "btn-add-to-scraper-queue") {
    deactivateBtn("btn-add-to-scraper-queue", "Adding to scraper...")
    res = await apiPut("/scraper/scrape-channels", body)
    activateBtn("btn-add-to-scraper-queue", handleScraperStartMulti, "Add to scraper queue")
    if (res.status === 404) {
      return resField.innerHTML = "Too few running jobs left to update. Start new scraper job."
    }
  }
  if (res.status === 400) {
    return resField.innerHTML = "Error on scraper start: Bad request."
  }
  if (res.status === 409) {
    return resField.innerHTML = "Error on scraper start: Scraper is busy."
  }
  if (res.status === 201) {
    let msg = e.target.id === "btn-start-scraper-multi" ? "Scaper started" : `${scrapeMultiRefs.length} channels added to queue`
    window.confirm(msg)
    scrapeMultiRefs = []
    return window.location = "/scraper"
  }
  return resField.innerHTML = "Unknown error on scraper start."
}

const handleScraperStartSingle = async e => {
  let channelRef = document.getElementById("channel-ref-single").value
  deactivateBtn("btn-start-scraper-single", "Scraper running...")
  let body = { "refs": [channelRef] }
  let res = await apiPost("/scraper/scrape-channels", body)
  activateBtn("btn-start-scraper-single", handleScraperStartSingle, "Start scraping")
  if (res.status === 400) {
    document.getElementById("scraper-response").textContent = "Error on scraper start: Bad request."
    return displayElement("scraper-response")
  }
  if (res.status === 409) {
    document.getElementById("scraper-response").textContent = "Error on scraper start: Scraper is busy."
    return displayElement("scraper-response")
  }
  if (res.status === 404) {
    return document.getElementById("scraper-response").textContent = "Error on scraper start: No clients available."
  }
  if (res.status === 201) {
    document.getElementById("scraper-response").textContent = `Scraper started for channel ${channelRef}`
    window.confirm("Scaper started")
    return window.location = "/scraper"
  }
  document.getElementById("scraper-response").textContent = "Unknown error on scraper start."
  return displayElement("scraper-response")
}

const handleGetScraperQueueLength = async e => {
  let resField = document.getElementById("scraper-res-multi")
  deactivateBtn("btn-get-scraper-queue-len", "Fetching number of remaining jobs...")
  let res = await apiGet("/scraper/scrape-channels")
  activateBtn("btn-get-scraper-queue-len", handleGetScraperQueueLength, "Show number of remaining jobs")
  if (res.status === 404) {
    return resField.innerHTML = "No scraping jobs scheduled."
  }
  if (res.status === 200) {
    return resField.innerHTML = `Ca. ${res["jobs"]} remaining in scraper queue`
  }
  return resField.innerHTML = "Unknown error."
}

const handleResetScraperQueue = async e => {
  let resField = document.getElementById("scraper-res-multi")
  deactivateBtn("reset-scraper-queue", "Reseting scraper queue...")
  let res = await apiDelete("/scraper/scrape-channels")
  activateBtn("reset-scraper-queue", handleResetScraperQueue, "Delete remaining jobs (Does not abort running scrapers)")
  if (res.status === 200) {
    return resField.innerHTML = "Reset of scraper queue successfull. Running scraper jobs continue."
  }
  return resField.innerHTML = "Unknown error."
}

activateBtn("btn-get-channel-meta-by-ref", handleGetMetaBtnClick, "Get metadata")
activateBtn("btn-start-scraper-single", handleScraperStartSingle, "Start scraping")
activateBtn("btn-start-scraper-multi", handleScraperStartMulti, "Start new scraper job")
activateBtn("btn-add-to-scraper-queue", handleScraperStartMulti, "Add to scraper queue")
activateBtn("btn-get-scraper-queue-len", handleGetScraperQueueLength, "Show number of remaining jobs")
activateBtn("reset-scraper-queue", handleResetScraperQueue, "Delete remaining jobs (Does not abort running scrapers)")
activateBtn("add-ref-btn", handleAddToRefBtnClick, "Add")
document.getElementById("channel-ref-files").addEventListener("change", handleRefFileUpload)
updateRefList()