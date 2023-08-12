import { activateBtn, deactivateBtn } from "./util.js"
import { apiGet, apiDelete } from "./api.js"

const handleGetActiveScrapersBtnClick = async e => {
  let scraperList = document.getElementById("active-scraper-list")
  scraperList.innerHTML = ""
  deactivateBtn("get-active-scrapers-btn", "Fetching active scrapers...")
  let res = await apiGet("/scraper/active-scrapers")
  activateBtn("get-active-scrapers-btn", handleGetActiveScrapersBtnClick, "Get active scrapers")
  if (res.status === 404) return scraperList.innerHTML = `<li>No active scrapers.</li><li>${res["errors"]} errors occured on last job.</li>`
  if (res.status === 200) {
    scraperList.innerHTML += `<li>${res["errors"]} errors occured on current job</li>`
    let activeScrapers = res["active_scrapers"]
    activeScrapers.forEach(element => {
      scraperList.innerHTML += `
    <li>
      <p>Phone number: ${element["phone"]}</p>
      <p>Scraping currently: ${element["cur_id"]}</p>
      <p>Finished last: ${element["last_scraped"]}</p>
      <button id="abort-scraper-${element["phone"]}" class="abort-scraper-btn" phone="${element["phone"]}">Abort scraper</button>
      <p id="abort-scraper-resp-${element["phone"]}"></p>
    </li>`
    });
    Array.from(document.getElementsByClassName("abort-scraper-btn")).forEach(btn => {
      activateBtn(btn.id, handleAbortScraperBtnClick, "Abort scraper")
    })
    return
  }
  scraperList.innerHTML = "<li>An unknown error occured.</li>"
}

const handleAbortScraperBtnClick = async e => {
  let phone = e.target.getAttribute("phone")
  let responseField = document.getElementById(`abort-scraper-resp-${phone}`)
  deactivateBtn(e.target.id, "Aborting scraper...")
  let res = await apiDelete("/scraper/abort-scraper", { "phone": phone })
  activateBtn(e.target.id, handleAbortScraperBtnClick, "Abort scraper")
  if (res.status === 400 || res.status === 404 || res.status === 200) return responseField.innerHTML = res.message
  responseField.innerHTML = "An unknown error occurred."
}

await handleGetActiveScrapersBtnClick()
activateBtn("get-active-scrapers-btn", handleGetActiveScrapersBtnClick, "Get active scrapers")