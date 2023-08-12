import { apiDelete, apiGet, apiPut } from "./api.js"
import { activateBtn, deactivateBtn } from "./util.js"

const handleResetBtnClick = async e => {
  let resField = document.getElementById("scraper-cfg-response")
  deactivateBtn(e.target.id, "Resetting cfg...")
  let res = await apiDelete("/scraper/config", {})
  activateBtn(e.target.id, handleResetBtnClick, "Reset to default")
  if (res.status === 409) return resField.innerHTML = res.message
  if (res.status === 200) {
    await getCurrentCfg()
    return resField.innerHTML = "Reset successfull"
  }
  resField.innerHTML = "Unknown error on reset."
}

const handleUpdateBtnClick = async e => {
  let resField = document.getElementById("scraper-cfg-response")
  let startDate = document.getElementById("cfg-start-date").value
  let endDate = document.getElementById("cfg-end-date").value
  let maxMsgs = Number(document.getElementById("cfg-max-num-msgs").value)
  let forceFull = document.getElementById("cfg-force-full").checked
  if (forceFull) {
    startDate = ""
    endDate = ""
    maxMsgs = 0
  }
  let body = { "start_date": startDate, "end_date": endDate, "max_msgs": maxMsgs, "force_full": forceFull }
  console.log(body);
  deactivateBtn(e.target.id, "Updating cfg...")
  let res = await apiPut("/scraper/config", body)
  activateBtn(e.target.id, handleUpdateBtnClick, "Update")
  if (res.status === 409 || res.status === 400) return resField.innerHTML = res.message
  if (res.status === 200) {
    console.log(res)
    await getCurrentCfg()
    return resField.innerHTML = "Update successfull"
  }
  resField.innerHTML = "Unknown error on update."
}

const getCurrentCfg = async () => {
  let resField = document.getElementById("current-cfg")
  let res = await apiGet("/scraper/config")
  if (res.status === 200) {
    resField.innerHTML = `
    <h3>Current scraping configuration</h3>
    <p>Start date: ${res["start_date"] ? res["start_date"] : "Not specified"}</p>
    <p>End date: ${res["end_date"] ? res["end_date"] : "Not specified"}</p>
    <p>Maximum messages: ${res["max_msgs"] === 0 ? "Whole channel" : res["max_msgs"]}</p>
    <p>Maximum messages: ${res["max_msgs"] === 0 ? "Whole channel" : res["max_msgs"]}</p>
    <p>Force full channel scrape: ${res["force_full"]}</p>`
    return
  }
  resField.innerHTML = "Unknown error when retrieving config"
}

activateBtn("defaut-cfg", handleResetBtnClick, "Reset to default")
activateBtn("update-cfg", handleUpdateBtnClick, "Update")
await getCurrentCfg()