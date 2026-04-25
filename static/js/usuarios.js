var senhaUserId = null;
var excluirUserId = null;

function alterarSenha(id, username) {
  senhaUserId = id;
  document.getElementById("senhaUsername").textContent = username;
  document.getElementById("novaSenha").value = "";
  new bootstrap.Modal(document.getElementById("alterarSenhaModal")).show();
}

function confirmarAlterarSenha() {
  var senha = document.getElementById("novaSenha").value;
  if (!senha) {
    alert("Digite a nova senha.");
    return;
  }
  fetch("/usuario/" + senhaUserId + "/alterar-senha", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: senha }),
  })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (data.success) {
        bootstrap.Modal.getInstance(
          document.getElementById("alterarSenhaModal"),
        ).hide();
        alert("Senha alterada com sucesso!");
      } else {
        alert("Erro: " + (data.error || ""));
      }
    })
    .catch(function () {
      alert("Erro ao alterar senha.");
    });
}

function excluirUsuario(id, username) {
  excluirUserId = id;
  document.getElementById("excluirUsername").textContent = username;
  new bootstrap.Modal(document.getElementById("confirmarExclusaoModal")).show();
}

function confirmarExcluir() {
  fetch("/usuario/" + excluirUserId + "/excluir", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (data.success) {
        bootstrap.Modal.getInstance(
          document.getElementById("confirmarExclusaoModal"),
        ).hide();
        location.reload();
      } else {
        alert("Erro: " + (data.error || ""));
      }
    })
    .catch(function () {
      alert("Erro ao excluir.");
    });
}
