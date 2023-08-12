import { apiPut } from "./api.js"
import { activateBtn, deactivateBtn } from "./util.js"

const handleUpdateBtnClick = async e => {
  let phone = document.getElementById("update-phone").value
  let username = document.getElementById("update-username").value
  let apiId = document.getElementById("update-api-id").value
  let apiHash = document.getElementById("update-api-hash").value
  if (!phone || !username || !apiId || !apiHash) return window.alert("Incomplete credentials given. Please fill all fields.")
  let body = { "phone": phone, "username": username, "api_id": apiId, "api_hash": apiHash }
  console.log(body);
  deactivateBtn("update-credentials-btn", `Updating credentials...`)
  let res = await apiPut("/credentials/edit", body)
  activateBtn("update-credentials-btn", handleUpdateBtnClick, "Update credentials")
  if (res.status === 400) {
    return window.alert("Error: Bad request.")
  }
  if (res.status === 404) {
    return window.alert(`Error: No credentials saved for number ${phone} or invalid number format.`)
  }
  if (res.status === 200) {
    document.getElementById("update-phone").value = res["phone"]
    document.getElementById("update-username").value = res["username"]
    document.getElementById("update-api-id").value = res["api_id"]
    document.getElementById("update-api-hash").value = res["api_hash"]
    return window.alert(`Updated credentials for phone number ${phone}.`)
  }
  window.alert("An unknown error occured.")
}

activateBtn("update-credentials-btn", handleUpdateBtnClick, "Update credentials")