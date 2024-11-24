function showModal() {
  document.getElementById("success-modal").style.display = "block";
}

function closeModal() {
  document.getElementById("success-modal").style.display = "none";
}

document.querySelector(".next-button").addEventListener("click", function (e) {
  e.preventDefault();
  showModal();
});
