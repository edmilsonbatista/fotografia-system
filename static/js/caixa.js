// Data padrão como hoje no modal de nova transação
document.addEventListener("DOMContentLoaded", function () {
  var dataInput = document.querySelector('input[name="data_transacao"]');
  if (dataInput) dataInput.value = new Date().toISOString().split("T")[0];
});

var transacaoIdEdicao = null;

function editarTransacao(id, tipo, valor, descricao, data, categoria) {
  transacaoIdEdicao = id;
  document.getElementById("editTransacaoId").value = id;
  document.getElementById("editTipo").value = tipo;
  document.getElementById("editValor").value = valor;
  document.getElementById("editDescricao").value = descricao;
  document.getElementById("editData").value = data;
  atualizarCategoriasEdit(tipo);
  setTimeout(function () {
    document.getElementById("editCategoria").value = categoria;
  }, 100);
  new bootstrap.Modal(document.getElementById("editarTransacaoModal")).show();
}

function salvarEdicaoTransacao() {
  var dados = {
    tipo: document.getElementById("editTipo").value,
    valor: parseFloat(document.getElementById("editValor").value),
    descricao: document.getElementById("editDescricao").value,
    data_transacao: document.getElementById("editData").value,
    categoria: document.getElementById("editCategoria").value,
  };
  fetch("/transacao/" + transacaoIdEdicao + "/editar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (data.success) {
        bootstrap.Modal.getInstance(
          document.getElementById("editarTransacaoModal"),
        ).hide();
        location.reload();
      } else {
        alert("Erro: " + (data.error || "Erro desconhecido"));
      }
    })
    .catch(function () {
      alert("Erro ao salvar.");
    });
}

function getCategorias(tipo) {
  if (tipo === "Entrada")
    return [
      "Pagamento de Cliente",
      "Sinal/Entrada",
      "Venda de Equipamento",
      "Outros",
    ];
  if (tipo === "Saída")
    return [
      "Equipamento",
      "Transporte",
      "Marketing",
      "Manutenção",
      "Alimentação",
      "Hospedagem",
      "Impostos",
      "Outros",
    ];
  return [];
}

function preencherSelect(select, categorias) {
  select.innerHTML = '<option value="">Selecione...</option>';
  categorias.forEach(function (cat) {
    var opt = document.createElement("option");
    opt.value = cat;
    opt.textContent = cat;
    select.appendChild(opt);
  });
}

function atualizarCategorias(tipo) {
  preencherSelect(
    document.getElementById("categoriaSelect"),
    getCategorias(tipo),
  );
}

function atualizarCategoriasEdit(tipo) {
  preencherSelect(
    document.getElementById("editCategoria"),
    getCategorias(tipo),
  );
}

function excluirTransacao(id, descricao) {
  document.getElementById("mensagemConfirmacao").innerHTML =
    'Deseja excluir a transação <strong>"' + descricao + '"</strong>?';
  var modal = new bootstrap.Modal(
    document.getElementById("confirmarExclusaoModal"),
  );
  modal.show();
  document.getElementById("btnConfirmarExclusao").onclick = function () {
    fetch("/transacao/" + id + "/excluir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.success) {
          modal.hide();
          location.reload();
        } else {
          alert("Erro: " + (data.error || ""));
        }
      })
      .catch(function () {
        alert("Erro ao excluir.");
      });
  };
}

function reverterPagamento(id, descricao) {
  if (
    confirm(
      'Reverter "' +
        descricao +
        '"?\n\nIsso remove o valor pago do evento e volta o status para Agendado.',
    )
  ) {
    fetch("/transacao/" + id + "/reverter", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.success) location.reload();
        else alert("Erro: " + (data.error || ""));
      })
      .catch(function () {
        alert("Erro ao reverter.");
      });
  }
}

// ===== FILTROS DO CAIXA =====
function aplicarFiltrosCaixa() {
  var busca = (document.getElementById("filtroBuscaCaixa") || {}).value || "";
  busca = busca.toLowerCase();
  var tipo = (document.getElementById("filtroTipoCaixa") || {}).value || "";
  var dataDe = (document.getElementById("filtroDataDeCaixa") || {}).value || "";
  var dataAte =
    (document.getElementById("filtroDataAteCaixa") || {}).value || "";
  var cat = (document.getElementById("filtroCategoriaCaixa") || {}).value || "";

  var rows = document.querySelectorAll("#tabelaCaixa tbody tr");
  var visiveis = 0;

  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var rDesc = row.getAttribute("data-desc") || "";
    var rTipo = row.getAttribute("data-tipo") || "";
    var rDate = row.getAttribute("data-date") || "";
    var rCat = row.getAttribute("data-cat") || "";

    var show = true;
    if (busca && rDesc.indexOf(busca) === -1) show = false;
    if (tipo && rTipo !== tipo) show = false;
    if (dataDe && rDate < dataDe) show = false;
    if (dataAte && rDate > dataAte) show = false;
    if (cat && rCat !== cat) show = false;

    row.style.display = show ? "" : "none";
    if (show) visiveis++;
  }

  var contador = document.getElementById("contadorFiltroCaixa");
  var total = document.getElementById("totalTransacoes");
  if (contador) contador.textContent = visiveis;
  if (total) total.textContent = visiveis;
}

function limparFiltrosCaixa() {
  var ids = [
    "filtroBuscaCaixa",
    "filtroTipoCaixa",
    "filtroDataDeCaixa",
    "filtroDataAteCaixa",
    "filtroCategoriaCaixa",
  ];
  for (var i = 0; i < ids.length; i++) {
    var el = document.getElementById(ids[i]);
    if (el) el.value = "";
  }
  aplicarFiltrosCaixa();
}
