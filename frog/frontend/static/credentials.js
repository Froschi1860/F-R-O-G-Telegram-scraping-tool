import { apiDelete, apiGet, apiPost } from "./api.js"
import { activateBtn, deactivateBtn } from "./util.js"

const updateSavedCredentials = async () => {
  let credList = document.getElementById("saved-credentials")
  credList.innerHTML = ""
  credList.classList.add("loader")
  let credentials = (await apiGet("/credentials"))["credentials"]
  credList.classList.remove("loader")
  if (!credentials || credentials.length === 0) return credList.innerHTML = "<li>No credentials saved</li>"
  credentials.forEach(el => {
    credList.innerHTML += `
    <li class="content-card">
      <div class="flex-column">
        <h4>Phone: ${el["phone"]}</h4>
        <p class="clearfix">Username: <span class="float-right">${el["username"]}</p>
        <p class="clearfix">API ID: <span class="float-right">${el["api_id"]}</p>
        <p class="clearfix">API hash: <span class="float-right">${el["api_hash"]}</p>
        <p class="clearfix">Authorized: <span class="float-right">${el["authorized"]}</p>
        ${el["flood_wait"] ? `<p class="clearfix">Flood wait until: <span class="float-right">${el["flood_wait"]}</p>` : ""} 
        <div>
          <button id="aut-${el["phone"]}" phone="${el["phone"]}" class="authorize-credentials-btn">Authorize</button>
          <button onclick="window.location.href='/credentials/edit?phone=${el["phone"]}'" class="edit-credentials-btn">Edit</button>
          <button id="delete-${el["phone"]}" phone="${el["phone"]}" class="delete-credentials-btn">Delete</button>
        </div>
        <p id="res-${el["phone"]}" class="response-field blink"></p>
      </div>
    </li>
    `
  })
  Array.from(document.getElementsByClassName("authorize-credentials-btn")).forEach(btn => {
    activateBtn(btn.id, handleAuthBtnClick, "Authorize")
  })
  Array.from(document.getElementsByClassName("delete-credentials-btn")).forEach(btn => {
    activateBtn(btn.id, handleDeleteBtnClick, "Delete")
  })
}

const handleAuthBtnClick = async e => {
  let phone = e.target.getAttribute("phone")
  let responseField = document.getElementById(`res-${phone}`)
  responseField.innerHTML = ""
  Array.from(document.getElementsByClassName("authorize-credentials-btn")).forEach(btn => {
    deactivateBtn(btn.id, `Authorizing ${phone}...`)
  })
  let res = await apiGet(`/authorize-client?phone=${phone}`)
  if (res.status === 401) {
    return window.location = `/authorize-client/verify-session?phone=${phone}`
  }
  Array.from(document.getElementsByClassName("authorize-credentials-btn")).forEach(btn => {
    activateBtn(btn.id, handleAuthBtnClick, "Authorize")
  })
  if (res.status === 500) {
    return responseField.innerHTML = "Error: "
      + (res["invalid_phone"] ? "Phone number is invalid. Delete the credentials and use a valid phone number." : "")
      + (res["invalid_api_id"] ? "API ID or API hash is invalid. Double-check your credentials." : "")
      + ((!res["invalid_phone"] && !res["invalid_api_id"]) ? "Internal server error." : "")
  }
  if (res.status === 400) {
    return responseField.innerHTML = "Error: Bad request."
  }
  if (res.status === 200) {
    return responseField.innerHTML = "Successfully authorized credentials."
  }
  responseField.innerHTML = "An unknown error occured."
}

const handleDeleteBtnClick = async e => {
  let phone = e.target.getAttribute("phone")
  if (!confirm(`Delete credentials for phone number ${phone}?`)) return
  deactivateBtn(phone, `Deleting credentials...`)
  let res = await apiDelete("/credentials", { "phone": phone })
  activateBtn(phone, handleDeleteBtnClick, "Delete")
  if (res.status === 400) {
    return window.alert("Error: Bad request.")
  }
  if (res.status === 404) {
    return window.alert(`Error: No credentials saved for phone number ${phone}.`)
  }
  if (res.status === 200) {
    await updateSavedCredentials()
    return window.alert(`Deleted credentials for phone number ${phone}.`)
  }
  window.alert("An unknown error occured.")
}

const handleAddCredentialsBtnClick = async e => {
  let phone = document.getElementById("new-cred-phone").value
  let username = document.getElementById("new-cred-username").value
  let apiId = document.getElementById("new-cred-api-id").value
  let apiHash = document.getElementById("new-cred-api-hash").value
  if (!phone || !username || !apiId || !apiHash) return window.alert("Incomplete credentials given. Please fill all fields.")
  deactivateBtn("add-credentials-btn", "Adding new credentials...")
  let body = { "phone": phone, "username": username, "api_id": apiId, "api_hash": apiHash }
  let res = await apiPost("/credentials", body)
  activateBtn("add-credentials-btn", handleAddCredentialsBtnClick, "Add new credentials")
  if (res.status === 400) {
    return window.alert("Error: Bad request.")
  }
  if (res.status === 409) {
    return window.alert("Error: Invalid phone number format or credentials with this number exist.")
  }
  if (res.status === 201) {
    document.getElementById("new-cred-phone").value = ""
    document.getElementById("new-cred-username").value = ""
    document.getElementById("new-cred-api-id").value = ""
    document.getElementById("new-cred-api-hash").value = ""
    await updateSavedCredentials()
    return window.alert(`Saved credentials:
    Phone: ${res["phone"]}
    Username: ${res["username"]}
    API ID: ${res["api_id"]}
    API hash: ${res["api_hash"]}`)
  }
  window.alert("An unknown error occured.")
}


await updateSavedCredentials()
activateBtn("add-credentials-btn", handleAddCredentialsBtnClick, "Add new credentials")