// Dark Mode — aplica no html (já feito pelo inline no head) e sincroniza body
(function () {
  var isDark = localStorage.getItem("darkMode") === "true";
  // html já tem a classe via script inline no head
  // Sincronizar body quando disponível
  if (isDark) document.body.classList.add("dark-mode");
  updateIcon();
})();

function toggleDarkMode() {
  // Ativar transição suave só ao clicar (não na carga)
  document.documentElement.classList.add("dark-mode-transition");

  var isDark = !document.documentElement.classList.contains("dark-mode");
  document.documentElement.classList.toggle("dark-mode", isDark);
  document.body.classList.toggle("dark-mode", isDark);
  localStorage.setItem("darkMode", isDark);
  updateIcon();

  // Remover classe de transição após completar
  setTimeout(function () {
    document.documentElement.classList.remove("dark-mode-transition");
  }, 400);
}

function updateIcon() {
  var icon = document.getElementById("darkModeIcon");
  if (!icon) return;
  icon.className = document.documentElement.classList.contains("dark-mode")
    ? "fas fa-sun"
    : "fas fa-moon";
}
