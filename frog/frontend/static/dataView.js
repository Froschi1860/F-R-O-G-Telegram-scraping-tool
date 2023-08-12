import { hideElement, displayElement, activateBtn, deactivateBtn, openModal, closeModal } from "./util.js"
import { apiGet, apiDelete, getMetaData, apiPost } from "./api.js"
import { updateKnownChannelMaps } from "./index.js"


const handleGetMetaByIdBtnClick = async e => {
  let metaField = document.getElementById("channel-meta")
  let channelId = document.getElementById("inp-channel-id").value
  hideElement("export-meta-section")
  metaField.textContent = ""
  metaField.innerHTML = ""
  if (channelId === "") {
    metaField.textContent = "Please enter a channel ID."
    return
  }
  if (isNaN(channelId) || Number(channelId) < 1) {
    metaField.textContent = "Channel ID must be a positive integer. For channel names or links use the channel reference field."
    return
  }
  deactivateBtn("btn-get-channel-meta-by-id", "Searching for metadata...")
  deactivateBtn("btn-get-channel-meta-by-ref", "Searching for metadata...")
  let url = `/data/meta-by-id?channel_id=${channelId}`
  if (await getMetaData(url)) displayElement("export-meta-section")
  activateBtn("btn-get-channel-meta-by-id", handleGetMetaByIdBtnClick, "Get metadata by ID")
  activateBtn("btn-get-channel-meta-by-ref", handleGetMetaByRefBtnClick, "Get metadata by reference")
}

const handleGetMetaByRefBtnClick = async e => {
  let metaField = document.getElementById("channel-meta")
  let channelRef = document.getElementById("inp-channel-ref").value
  hideElement("export-meta-section")
  metaField.textContent = ""
  metaField.innerHTML = ""
  if (channelRef === "") {
    metaField.textContent = "Please enter a channel reference."
    return
  }
  if (!isNaN(channelRef)) {
    metaField.textContent = "Channel reference cannot be a number. For channel ID use the ID field instead."
    return
  }
  deactivateBtn("btn-get-channel-meta-by-id", "Searching for metadata...")
  deactivateBtn("btn-get-channel-meta-by-ref", "Searching for metadata...")
  let url = `/data/meta-by-ref?channel_ref=${channelRef}`
  if (await getMetaData(url)) displayElement("export-meta-section")
  activateBtn("btn-get-channel-meta-by-id", handleGetMetaByIdBtnClick, "Get metadata by ID")
  activateBtn("btn-get-channel-meta-by-ref", handleGetMetaByRefBtnClick, "Get metadata by reference")
}

const handleExportMetaBtnClick = async e => {
  let channelId = document.getElementById("channel-id-meta").value
  let responseField = document.getElementById("export-meta-info")
  if (!channelId) {
    responseField.innerHTML = "Enter an ID to start"
    return
  }
  if (isNaN(channelId) || Number(channelId) < 1) {
    responseField.innerHTML = "ID must be a positive integer."
    return
  }
  deactivateBtn("export-meta", "Exporting...")
  let url = `/data/export-meta?channel_id=${channelId}`
  responseField.innerHTML = "Exporting data..."
  let res = await apiGet(url)
  if (res.status === 300) {
    let overwrite = confirm("The file already exists. Do you want to overwrite it?")
    if (!overwrite) {
      responseField.innerHTML = `Existing file was not overwritten. Output directory: ${res.path}`
      activateBtn("export-meta", handleExportMetaBtnClick, "Export meta as JSON")
      return
    }
    res = await apiGet(url += "&overwrite=true")
  }
  if (res.status === 400) {
    responseField.innerHTML = "Error: Bad request."
    activateBtn("export-meta", handleExportMetaBtnClick, "Export meta as JSON")
    return
  }
  if (res.status === 404) {
    responseField.innerHTML = "Error: Channel not found."
    activateBtn("export-meta", handleExportMetaBtnClick, "Export meta as JSON")
    return
  }
  if (res.status === 409) {
    responseField.innerHTML = "Error: Output directory does not exist."
    activateBtn("export-meta", handleExportMetaBtnClick, "Export meta as JSON")
    return
  }
  if (res.status === 500) {
    responseField.innerHTML = "Error: Internal server error. Refer to error log."
    activateBtn("export-meta", handleExportMetaBtnClick, "Export meta as JSON")
    return
  }
  if (res.status === 200) {
    responseField.innerHTML = `Export successful. Output directory: ${res.path}`
    activateBtn("export-meta", handleExportMetaBtnClick, "Export meta as JSON")
    return
  }
  responseField.innerHTML = `An unknown error occured.`
  activateBtn("export-meta", handleExportMetaBtnClick, "Export meta as JSON")
}

const handleDeleteChannelBtnClick = e => {
  let channelId = document.getElementById("inp-channel-id-msgs").value
  let responseField = document.getElementById("export-msgs-info")
  if (!channelId) {
    return responseField.innerHTML = "Enter an ID to start"
  }
  if (isNaN(channelId) || Number(channelId) < 1) {
    return responseField.innerHTML = "ID must be a positive integer."
  }
  let modalContent = `
    <div id="delete-modal-content">
      <label for="include-meta">Include metadata?</label>
      <input type="checkbox" name="include-meta" id="include-meta">
      <button id="btn-confirm-delete-channel">Delete</button>
    </div>`
  openModal(`Delete channel ${channelId} from database`, modalContent)
  activateBtn("btn-confirm-delete-channel", handleConfirmDeleteChannelBtnClick, "Delete")
}

const handleConfirmDeleteChannelBtnClick = async e => {
  let channelId = document.getElementById("inp-channel-id-msgs").value
  let responseField = document.getElementById("export-msgs-info")
  let includeMeta = document.getElementById("include-meta").checked
  if (!channelId) return responseField.innerHTML = "Enter an ID to start"
  if (isNaN(channelId) || Number(channelId) < 1) return responseField.innerHTML = "ID must be a positive integer."
  let body = { "channel_id": Number(channelId), "include_meta": includeMeta }
  deactivateBtn("btn-confirm-delete-channel", `Deleting channel ${channelId}...`)
  let res = await apiDelete("/data/delete-channel", body)
  if (res.status === 400) {
    responseField.innerHTML = `Error: Bad request.`
    return closeModal()
  }
  if (res.status === 404) {
    responseField.innerHTML = `Error: Channel not found.`
    return closeModal()
  }
  if (res.status === 200) {
    await updateKnownChannelMaps()
    responseField.innerHTML = `Deleted channel ${channelId}. `
      + (includeMeta ? "Metadata deleted. " : "")
    return closeModal()
  }
  responseField.innerHTML = `Unknown error.`
  return closeModal()
}

const handleDeleteNameIdMappingsBtnClick = async e => {
  let channelId = document.getElementById("delete-mappings-id").value
  let responseField = document.getElementById("name-id-map-response")
  if (!channelId) {
    return responseField.innerHTML = "Enter an ID to start"
  }
  if (isNaN(channelId) || Number(channelId) < 1) {
    return responseField.innerHTML = "ID must be a positive integer."
  }
  let modalContent = `
    <div id="delete-modal-content">
      <button id="btn-confirm-delete-mappings">Delete</button>
    </div>`
  openModal(`Delete mappings for ${channelId}`, modalContent)
  activateBtn("btn-confirm-delete-mappings", handleConfirmDeleteMappingsBtnClick, "Delete")
}

const handleConfirmDeleteMappingsBtnClick = async e => {
  let channelId = document.getElementById("delete-mappings-id").value
  let responseField = document.getElementById("name-id-map-response")
  if (!channelId) return responseField.innerHTML = "Enter an ID to start"
  if (isNaN(channelId) || Number(channelId) < 1) return responseField.innerHTML = "ID must be a positive integer."
  let body = { "channel_id": Number(channelId) }
  deactivateBtn("btn-confirm-delete-mappings", `Deleting mappings for ${channelId}...`)
  let res = await apiDelete("/data/delete-name-id-maps", body)
  if (res.status === 400 || res.status === 404) {
    responseField.innerHTML = res.message
    return closeModal()
  }
  if (res.status === 200) {
    responseField.innerHTML = res.message
    await updateKnownChannelMaps()
    return closeModal()
  }
  responseField.innerHTML = "An unknown error occured"
  return closeModal()
}

const handleExportNameIdMappingsBtnClick = async e => {
  let responseField = document.getElementById("name-id-map-response")
  deactivateBtn("export-mappings-btn", "Exporting...")
  let res = await apiPost("/data/export-mappings", {})
  activateBtn("export-mappings-btn", handleExportNameIdMappingsBtnClick, "Export")
  if (res.status === 201) return responseField.innerHTML = `Export successful. Output directory: ${res["output_path"]}`
  responseField.innerHTML = res.message
}

activateBtn("export-mappings-btn", handleExportNameIdMappingsBtnClick, "Export")
activateBtn("delete-mappings-btn", handleDeleteNameIdMappingsBtnClick, "Delete")
activateBtn("export-meta", handleExportMetaBtnClick, "Export meta as JSON")
activateBtn("btn-delete-channel", handleDeleteChannelBtnClick, "Delete channel")
activateBtn("btn-get-channel-meta-by-id", handleGetMetaByIdBtnClick, "Get metadata by ID")
activateBtn("btn-get-channel-meta-by-ref", handleGetMetaByRefBtnClick, "Get metadata by reference")
