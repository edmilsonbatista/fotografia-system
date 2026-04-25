// Dark Mode Toggle — persiste no localStorage
(function () {
  var saved = localStorage.getItem("darkMode");
  if (saved === "true") document.body.classList.add("dark-mode");
  updateIcon();
})();

function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  var isDark = document.body.classList.contains("dark-mode");
  localStorage.setItem("darkMode", isDark);
  updateIcon();
}

function updateIcon() {
  var icon = document.getElementById("darkModeIcon");
  if (!icon) return;
  var isDark = document.body.classList.contains("dark-mode");
  icon.className = isDark ? "fas fa-sun" : "fas fa-moon";
}
