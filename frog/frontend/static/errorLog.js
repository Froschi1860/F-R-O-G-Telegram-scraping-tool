import { activateBtn, deactivateBtn } from "./util.js"
import { apiPost, apiDelete } from "./api.js"

const handleExportBtnClick = async e => {
  let responseField = document.getElementById("error-log-response")
  deactivateBtn("export-error-log", "Exporting...")
  let res = await apiPost("/error-log/export", {})
  activateBtn("export-error-log", handleExportBtnClick, "Export error log")
  if (res.status === 201) return responseField.innerHTML = `Export successfull. Output directory: ${res["output_path"]}`
  return responseField.innerHTML = res.message
}

const handleDeleteBtnClick = async e => {
  let responseField = document.getElementById("error-log-response")
  if (!confirm("Confirm reset of error log")) return
  deactivateBtn("delete-error-log", "Deleting...")
  let res = await apiDelete("/error-log", {})
  activateBtn("delete-error-log", handleDeleteBtnClick, "Delete error log")
  responseField.innerHTML = res.message
}

activateBtn("delete-error-log", handleDeleteBtnClick, "Delete error log")
activateBtn("export-error-log", handleExportBtnClick, "Export error log")