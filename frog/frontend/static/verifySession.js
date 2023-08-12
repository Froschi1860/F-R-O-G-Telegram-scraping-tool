import { apiGet, apiPost } from "./api.js"
import { activateBtn, deactivateBtn } from "./util.js"

const handleSubmitVerCodeBtnClick = async e => {
  let verCode = document.getElementById("verification-code").value
  let phone = document.getElementById("phone").value.replace(" ", "+")
  console.log(phone);
  let responseField = document.getElementById("response")
  responseField.innerHTML = ""
  if (!verCode || isNaN(verCode) || Number(verCode) < 0) return responseField.innerHTML = "The code must be a positive integer."
  deactivateBtn("send-verification-code-btn", "Checking code...")
  let res = await apiPost("/authorize-client", { "verification_code": verCode, "phone": phone })
  activateBtn("send-verification-code-btn", e => window.location = "/home", "Back to start")
  if (res.status === 400) {
    return responseField.innerHTML = "Error: Bad request."
  }
  if (res.status === 500) {
    return responseField.innerHTML = "Error: "
      + (res["invalid_phone"] ? "Phone number is invalid. Delete the credentials and use a valid phone number." : "")
      + (res["invalid_api_id"] ? "API ID or API hash is invalid. Double-check your credentials." : "")
      + ((!res["invalid_phone"] && !res["invalid_api_id"]) ? "Internal server error." : "")
  }
  if (res.status === 401) {
    responseField.innerHTML = `Wrong code entered. <button id="retry-auth"></button>`
    return activateBtn("retry-auth", async e => {
      await apiGet(`/authorize-client?phone=${res["phone"]}`)
      deactivateBtn("retry-auth", "Resending code...")
      document.getElementById("verification-code").value = ""
      responseField.innerHTML = ""
      deactivateBtn("send-verification-code-btn")
      activateBtn("send-verification-code-btn", handleSubmitVerCodeBtnClick, "Check code")
    }, "Resend code")
  }
  if (res.status === 200) {
    return responseField.innerHTML = "Credentials successully authorized."
  }
  responseField.innerHTML = "An unknown error occured."
}

activateBtn("send-verification-code-btn", handleSubmitVerCodeBtnClick, "Check code")