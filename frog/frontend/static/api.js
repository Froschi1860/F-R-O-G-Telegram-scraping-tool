const apiGet = async url => {
  let res = await fetch(url)
  let body = await res.json()
  body.status = res.status
  return body
}

const apiPost = async (url, body) => {
  let res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    "body": JSON.stringify(body)
  })
  let payload = await res.json()
  payload.status = res.status
  return payload
}

const apiPut = async (url, body) => {
  let res = await fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    "body": JSON.stringify(body)
  })
  let payload = await res.json()
  payload.status = res.status
  return payload
}

const apiDelete = async (url, body) => {
  let res = await fetch(url, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json"
    },
    "body": JSON.stringify(body)
  })
  let payload = await res.json()
  payload.status = res.status
  return payload
}

const getMetaData = async (url) => {
  let metaField = document.getElementById("channel-meta")
  let res = await apiGet(url)
  if (res.status === 400) {
    metaField.textContent = "ERROR: Bad request. Please retry."
    return
  }
  if (res.status === 409) {
    metaField.textContent = "ERROR: Telethon client busy. Please retry after scraping is done."
    return
  }
  if (res.status === 404) {
    metaField.textContent = "ERROR: Channel not found."
    return
  }
  if (res.status === 200) {
    metaField.innerHTML = `
    <h4>Channel ID: <input id="channel-id-meta" value="${res["channel_id"]}" readonly></h4>
    <p>Known references: <span>${res["refs"]}</span></p>
    <p>Last message ID: <span>${res["last_msg_id"]}</span></p>
    <p>Channel accessible: <span>${res["accessible"]}</span></p>
    <p>Last accessed on: <span>${res["last_access"]}</span></p>
    <p>Number of active users (export metadata for list of IDs): <span>${res["channel_users"].length}</span></p>
    `
    return true
  }
  metaField.textContent = "ERROR: An unkown error occured."
}

export { apiGet, apiPost, apiPut, apiDelete, getMetaData }