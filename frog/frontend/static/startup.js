import { apiGet } from "./api.js"


await apiGet("/credentials") // Authenticate registered credentials
window.location = "/home"