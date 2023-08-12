const hideElement = (htmlId) => {
  let el = document.getElementById(htmlId)
  el.classList.add("hidden")
}

const displayElement = (htmlId) => {
  let el = document.getElementById(htmlId)
  el.classList.remove("hidden")
}

const activateBtn = (htmlId, eventHandler, btnText) => {
  let btn = document.getElementById(htmlId)
  if (!btn || !eventHandler) return
  if (btnText) btn.textContent = btnText
  btn.classList.remove("inactiveBtn")
  btn.addEventListener("click", eventHandler)
}

const deactivateBtn = (htmlId, btnText) => {
  let btn = document.getElementById(htmlId)
  if (!btn) return
  if (btnText) btn.textContent = btnText
  btn.classList.add("inactiveBtn")
  btn.replaceWith(btn.cloneNode(true))
}

const openModal = (modalTitle, modalContent) => {
  let modal = document.getElementById("modal")
  let closeModal = document.getElementById("close-modal")
  let title = document.getElementById("modal-title")
  let content = document.getElementById("modal-content")
  title.innerHTML = modalTitle
  content.innerHTML = modalContent
  modal.style.display = "block"
  closeModal.onclick = function () {
    modal.style.display = "none"
  }
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none"
    }
  }
}

const closeModal = () => {
  let modal = document.getElementById("modal")
  modal.style.display = "none"
}

export { hideElement, displayElement, activateBtn, deactivateBtn, openModal, closeModal }