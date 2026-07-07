// CSRF token helper — adiciona token em todas as requisições fetch POST
(function () {
  var token = document.querySelector('meta[name="csrf-token"]');
  if (!token) return;
  var csrfToken = token.getAttribute("content");

  // Interceptar fetch para adicionar CSRF token automaticamente
  var originalFetch = window.fetch;
  window.fetch = function (url, options) {
    options = options || {};
    if (options.method && options.method.toUpperCase() !== "GET") {
      options.headers = options.headers || {};
      if (options.headers instanceof Headers) {
        options.headers.set("X-CSRFToken", csrfToken);
      } else {
        options.headers["X-CSRFToken"] = csrfToken;
      }
    }
    return originalFetch.call(this, url, options);
  };
})();
