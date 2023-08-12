import { activateBtn, deactivateBtn, displayElement, hideElement, openModal } from "./util.js"
import { apiGet, apiPost } from "./api.js"
import { allKnownChannelIds } from "./index.js"

let msgs = []


const handleExportAllBtnClick = async e => {
  const includeMeta = document.getElementById("export-all-include-meta").checked
  const responseField = document.getElementById("export-all-info")
  responseField.innerHTML = ""
  deactivateBtn("export-all-json", "Exporting...")
  deactivateBtn("export-all-csv", "Exporting...")
  let filetype = ""
  if (e.target.id == "export-all-json") filetype = "json"
  if (e.target.id == "export-all-csv") filetype = "csv"
  let url = "/data/export-multiple"
  let body = {
    "channel_ids": allKnownChannelIds,
    "filetype": filetype,
    "include_meta": includeMeta
  }
  let res = await apiPost(url, body)
  if (res.status === 400) {
    responseField.innerHTML = "Error: Bad request"
    activateBtn("export-all-json", handleExportAllBtnClick, "As JSON")
    activateBtn("export-all-csv", handleExportAllBtnClick, "As CSV")
    return
  }
  if (res.status === 409) {
    responseField.innerHTML = "Error: Output directory does not exist"
    activateBtn("export-all-json", handleExportAllBtnClick, "As JSON")
    activateBtn("export-all-csv", handleExportAllBtnClick, "As CSV")
    return
  }
  if (res.status === 500) {
    responseField.innerHTML = `Error: Internal server error. Not found: ${res["not_found"]}; Output path: ${res["path"]}; Written:<ul>`
    res["written"].forEach(el => responseField.innerHTML += `<li>${el}</li>`)
    responseField.innerHTML += "</ul>"
    activateBtn("export-all-json", handleExportAllBtnClick, "As JSON")
    activateBtn("export-all-csv", handleExportAllBtnClick, "As CSV")
    return
  }
  if (res.status === 200) {
    responseField.innerHTML = "No channels exported."
    activateBtn("export-all-json", handleExportAllBtnClick, "As JSON")
    activateBtn("export-all-csv", handleExportAllBtnClick, "As CSV")
    return
  }
  if (res.status === 201) {
    responseField.innerHTML = `Success. Not found: ${res["not_found"]}; Output path: ${res["path"]}; Written:<ul>`
    res["written"].forEach(el => responseField.innerHTML += `<li>${el}</li>`)
    responseField.innerHTML += "</ul>"
    activateBtn("export-all-json", handleExportAllBtnClick, "As JSON")
    activateBtn("export-all-csv", handleExportAllBtnClick, "As CSV")
    return
  }
  responseField.innerHTML = "An unknown error occured."
  activateBtn("export-all-json", handleExportAllBtnClick, "As JSON")
  activateBtn("export-all-csv", handleExportAllBtnClick, "As CSV")
}

const handleExportBtnClick = async e => {
  let channelId = document.getElementById("inp-channel-id-msgs").value
  let responseField = document.getElementById("export-msgs-info")
  if (!channelId) {
    responseField.innerHTML = "Enter an ID to start"
    return
  }
  if (isNaN(channelId) || Number(channelId) < 1) {
    responseField.innerHTML = "ID must be a positive integer."
    return
  }
  deactivateBtn("export-csv", "Exporting...")
  deactivateBtn("export-json", "Exporting...")
  let url = `/data/export-msgs?channel_id=${channelId}&filetype=`
  if (e.target.id === "export-csv") url += "csv"
  if (e.target.id === "export-json") url += "json"
  responseField.innerHTML = "Exporting data..."
  let res = await apiGet(url)
  if (res.status === 300) {
    let overwrite = confirm("The file already exists. Do you want to overwrite it?")
    if (!overwrite) {
      responseField.innerHTML = `Existing file was not overwritten. Output directory: ${res.path}`
      activateBtn("export-csv", handleExportBtnClick, "Export messages as CSV")
      activateBtn("export-json", handleExportBtnClick, "Export messages as JSON")
      return
    }
    res = await apiGet(url += "&overwrite=true")
  }
  if (res.status === 400) {
    responseField.innerHTML = "Error: Bad request."
    activateBtn("export-csv", handleExportBtnClick, "Export messages as CSV")
    activateBtn("export-json", handleExportBtnClick, "Export messages as JSON")
    return
  }
  if (res.status === 404) {
    responseField.innerHTML = "Error: Channel not found."
    activateBtn("export-csv", handleExportBtnClick, "Export messages as CSV")
    activateBtn("export-json", handleExportBtnClick, "Export messages as JSON")
    return
  }
  if (res.status === 409) {
    responseField.innerHTML = "Error: Output directory does not exist."
    activateBtn("export-csv", handleExportBtnClick, "Export messages as CSV")
    activateBtn("export-json", handleExportBtnClick, "Export messages as JSON")
    return
  }
  if (res.status === 500) {
    responseField.innerHTML = "Error: Internal server error. Refer to error log."
    activateBtn("export-csv", handleExportBtnClick, "Export messages as CSV")
    activateBtn("export-json", handleExportBtnClick, "Export messages as JSON")
    return
  }
  if (res.status === 200) {
    responseField.innerHTML = `Export successful. Output directory: ${res.path}`
    activateBtn("export-csv", handleExportBtnClick, "Export messages as CSV")
    activateBtn("export-json", handleExportBtnClick, "Export messages as JSON")
    return
  }
  responseField.innerHTML = `An unknown error occured.`
  activateBtn("export-csv", handleExportBtnClick, "Export messages as CSV")
  activateBtn("export-json", handleExportBtnClick, "Export messages as JSON")
}

const handleMsgQuery = async (e) => {
  let channelId = document.getElementById("inp-channel-id-msgs").value
  let responseField = document.getElementById("msgs-channel-info")
  let table = document.getElementById("channel-msgs-body")
  table.innerHTML = ""
  if (!channelId) {
    return responseField.innerHTML = "Enter an ID to start"
  }
  if (isNaN(channelId) || Number(channelId) < 1) {
    return responseField.innerHTML = "ID must be a positive integer."
  }
  deactivateBtn("btn-get-channel-msgs", "Retrieving messages...")
  let res = await apiGet(`/data/msgs-by-id?channel_id=${channelId}`)
  if (res.status === 400) {
    responseField.innerHTML = "Error: Bad request."
    activateBtn("btn-get-channel-msgs", handleMsgQuery, "Show messages")
    return
  }
  if (res.status === 404) {
    responseField.innerHTML = "Error: No messages found."
    activateBtn("btn-get-channel-msgs", handleMsgQuery, "Show messages")
    return
  }
  if (res.status === 200) {
    msgs = res["msgs"]
    if (!msgs || msgs.length === 0) {
      activateBtn("btn-get-channel-msgs", handleMsgQuery, "Show messages")
      return table.innerHTML = "<tr><td>No messages found.</td></tr>"
    }
    msgs.forEach(element => {
      table.innerHTML += `
      <tr>
        <td class="table-id">${element["id"]}</td>
        <td class="table-type">${element["type"]}</td>
        <td class="table-msg">${element["message"] || "N/A"}</td>
        <td class="table-details"><button id="${element["id"]}" class="showMsgDetails"></button></td>
      </tr>`
    })
    msgs.forEach(msg => activateBtn(`${msg["id"]}`, handleDetailsBtn, "Details"))
    activateBtn("btn-get-channel-msgs", handleMsgQuery, "Show messages")
    return
  }
  responseField.innerHTML = "Error: An unexpected error occured."
  activateBtn("btn-get-channel-msgs", handleMsgQuery, "Show messages")
}

const handleDetailsBtn = e => {
  let msg = msgs.find(msg => msg.id == e.target.getAttribute("id"))
  openModal(`Details for message ${msg.id}`, `<pre><code>${JSON.stringify(msg, null, 4)}</code></pre>`)
}


activateBtn("export-csv", handleExportBtnClick, "Export messages as CSV")
activateBtn("export-json", handleExportBtnClick, "Export messages as JSON")
activateBtn("btn-get-channel-msgs", handleMsgQuery, "Show messages")
activateBtn("export-all-json", handleExportAllBtnClick, "As JSON")
activateBtn("export-all-csv", handleExportAllBtnClick, "As CSV")