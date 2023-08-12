import { apiGet } from "./api.js"

let allKnownChannelIds = []

const updateKnownChannelMaps = async () => {
  let nameIdMaps = await apiGet("/data/all-channels-refs")
  let channelListId = document.getElementById("known-channels-id")
  let channelListRef = document.getElementById("known-channels-ref")
  allKnownChannelIds = Array.from(new Set(nameIdMaps.map(e => e["channel_id"])))
  channelListId.innerHTML = ""
  nameIdMaps.forEach(mapping => {
    channelListId.innerHTML += `
    <option value="${mapping["channel_id"]}">Reference: ${mapping["channel_ref"]}</option>
    `
  })
  channelListRef.innerHTML = ""
  nameIdMaps.forEach(mapping => {
    channelListRef.innerHTML += `
    <option value="${mapping["channel_ref"]}"></option>
    `
  })
}

await updateKnownChannelMaps()

export { allKnownChannelIds, updateKnownChannelMaps }