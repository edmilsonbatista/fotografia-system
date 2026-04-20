// ===== FILTROS =====
function aplicarFiltros() {
  var cliente = document.getElementById("filtroCliente").value.toLowerCase();
  var servico = document.getElementById("filtroServico").value;
  var dataDe = document.getElementById("filtroDataDe").value;
  var dataAte = document.getElementById("filtroDataAte").value;
  var status = document.getElementById("filtroStatus").value;

  var rows = document.querySelectorAll("#tabelaEventos tbody tr");
  var visiveis = 0;
  var somaNegocia = 0;
  var somaPago = 0;

  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var rCliente = row.getAttribute("data-cliente") || "";
    var rServico = row.getAttribute("data-servico") || "";
    var rDate = row.getAttribute("data-date") || "";
    var rStatus = row.getAttribute("data-status") || "";

    var show = true;
    if (cliente && rCliente.indexOf(cliente) === -1) show = false;
    if (servico && rServico !== servico) show = false;
    if (dataDe && rDate < dataDe) show = false;
    if (dataAte && rDate > dataAte) show = false;
    if (status && rStatus !== status) show = false;

    row.style.display = show ? "" : "none";
    if (show) {
      visiveis++;
      var cells = row.querySelectorAll("td");
      somaNegocia += parseMoneyBR(cells[4]);
      somaPago += parseMoneyBR(cells[5]);
    }
  }

  document.getElementById("contadorFiltro").textContent = visiveis;
  document.getElementById("totalEventos").textContent = visiveis;
  document.getElementById("totalNegociado").textContent =
    formatMoneyBR(somaNegocia);
  document.getElementById("totalPago").textContent = formatMoneyBR(somaPago);
}

function limparFiltros() {
  document.getElementById("filtroCliente").value = "";
  document.getElementById("filtroServico").value = "";
  document.getElementById("filtroDataDe").value = "";
  document.getElementById("filtroDataAte").value = "";
  document.getElementById("filtroStatus").value = "";
  aplicarFiltros();
}

function parseMoneyBR(cell) {
  if (!cell) return 0;
  var txt = cell.textContent || "";
  txt = txt
    .replace("R$", "")
    .replace(/\s/g, "")
    .replace(/\./g, "")
    .replace(",", ".");
  return parseFloat(txt) || 0;
}

function formatMoneyBR(val) {
  var parts = val.toFixed(2).split(".");
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return "R$ " + parts.join(",");
}

// ===== ORDENAÇÃO POR DATA =====
var ordemDataAsc = true;
function ordenarPorData() {
  var tbody = document.querySelector("#tabelaEventos tbody");
  var rows = Array.from(tbody.querySelectorAll("tr"));
  rows.sort(function (a, b) {
    var dA = a.getAttribute("data-date") || "";
    var dB = b.getAttribute("data-date") || "";
    if (ordemDataAsc) return dA < dB ? -1 : dA > dB ? 1 : 0;
    return dA > dB ? -1 : dA < dB ? 1 : 0;
  });
  rows.forEach(function (row) {
    tbody.appendChild(row);
  });
  ordemDataAsc = !ordemDataAsc;
  var icon = document.getElementById("iconOrdemData");
  icon.className = ordemDataAsc ? "fas fa-sort-up" : "fas fa-sort-down";
  aplicarFiltros();
}

// ===== DETALHES =====
function verDetalhes(
  cliente,
  tipoServico,
  dataEvento,
  valorNegociado,
  valorPago,
  status,
  dataCadastro,
  observacoes,
  ensaiosExtras,
) {
  document.getElementById("detalheCliente").textContent =
    cliente || "Cliente não informado";
  document.getElementById("detalheTipoServico").textContent = tipoServico;
  document.getElementById("detalheDataEvento").textContent = dataEvento;
  document.getElementById("detalheEnsaiosExtras").textContent =
    ensaiosExtras || "Nenhum";
  document.getElementById("detalheValorNegociado").textContent =
    "R$ " + valorNegociado.toFixed(2).replace(".", ",");
  document.getElementById("detalheValorPago").textContent =
    "R$ " + valorPago.toFixed(2).replace(".", ",");
  document.getElementById("detalheStatus").textContent = status;
  document.getElementById("detalheDataCadastro").textContent = dataCadastro;

  var obsContainer = document.getElementById("detalheObservacoesContainer");
  var obsTexto = document.getElementById("detalheObservacoes");

  if (observacoes && observacoes.trim() !== "" && observacoes !== "None") {
    obsTexto.textContent = observacoes;
    obsContainer.style.display = "block";
  } else {
    obsContainer.style.display = "none";
  }

  var modal = new bootstrap.Modal(document.getElementById("detalhesModal"));
  modal.show();
}

// ===== MOEDA =====
function formatarCampoMoeda(campo) {
  var valor = parseFloat(campo.value);
  if (!isNaN(valor)) {
    campo.value = valor.toFixed(2);
  }
}

// ===== ENSAIOS EXTRAS (EDIÇÃO) =====
function toggleEditEnsaiosExtras() {
  var checkbox = document.getElementById("editTemEnsaiosExtras");
  var options = document.getElementById("editEnsaiosExtrasOptions");

  if (checkbox.checked) {
    options.style.display = "block";
  } else {
    options.style.display = "none";
    document
      .querySelectorAll('input[name="editTipoEnsaio"]')
      .forEach(function (radio) {
        radio.checked = false;
      });
    document.getElementById("editOutrosEnsaioField").style.display = "none";
    document.getElementById("editOutrosEnsaioTexto").value = "";
  }
}

function toggleEditOutrosEnsaio() {
  var outrosRadio = document.getElementById("editOutros");
  var outrosField = document.getElementById("editOutrosEnsaioField");

  if (outrosRadio.checked) {
    outrosField.style.display = "block";
  } else {
    outrosField.style.display = "none";
    document.getElementById("editOutrosEnsaioTexto").value = "";
  }
}

// ===== PAGAMENTO =====
var eventoIdPagamento = null;
var eventoIdExclusao = null;
var eventoIdEdicao = null;

function registrarPagamento(eventoId, valorRestante) {
  eventoIdPagamento = eventoId;
  document.getElementById("valorPagamento").value = valorRestante.toFixed(2);
  new bootstrap.Modal(document.getElementById("pagamentoModal")).show();
}

function confirmarPagamento() {
  var valor = parseFloat(document.getElementById("valorPagamento").value);

  if (!valor || valor <= 0) {
    alert("Por favor, insira um valor válido.");
    return;
  }

  fetch("/evento/" + eventoIdPagamento + "/pagar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ valor: valor }),
  })
    .then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then(function (data) {
      if (data.success) {
        bootstrap.Modal.getInstance(
          document.getElementById("pagamentoModal"),
        ).hide();
        location.reload();
      } else {
        alert("Erro: " + (data.error || "Erro desconhecido"));
      }
    })
    .catch(function (error) {
      alert("Erro ao processar pagamento: " + error.message);
    });
}

// ===== EDITAR EVENTO =====
function editarEvento(
  eventoId,
  cliente,
  tipoServico,
  dataEvento,
  valorNegociado,
  valorPago,
  status,
  observacoes,
  ensaiosExtras,
) {
  eventoIdEdicao = eventoId;

  document.getElementById("editCliente").value = cliente;
  document.getElementById("editTipoServico").value = tipoServico;
  document.getElementById("editDataEvento").value = dataEvento;
  document.getElementById("editValorNegociado").value = valorNegociado;
  document.getElementById("editValorPago").value = valorPago;
  document.getElementById("editStatus").value = status;
  document.getElementById("editObservacoes").value = observacoes;

  var temEnsaios = ensaiosExtras && ensaiosExtras !== "Nenhum";
  document.getElementById("editTemEnsaiosExtras").checked = temEnsaios;

  if (temEnsaios) {
    document.getElementById("editEnsaiosExtrasOptions").style.display = "block";
    var opcoesPredefinidas = [
      "Pre-Wedding",
      "Book Fotográfico (15 anos)",
      "Ensaio Casal",
      "Ensaio Individual",
      "Ensaio Família",
    ];
    var radioEncontrado = opcoesPredefinidas.find(function (opcao) {
      return opcao === ensaiosExtras;
    });

    if (radioEncontrado) {
      document.querySelector(
        'input[name="editTipoEnsaio"][value="' + radioEncontrado + '"]',
      ).checked = true;
    } else {
      document.getElementById("editOutros").checked = true;
      document.getElementById("editOutrosEnsaioField").style.display = "block";
      document.getElementById("editOutrosEnsaioTexto").value = ensaiosExtras;
    }
  } else {
    document.getElementById("editEnsaiosExtrasOptions").style.display = "none";
  }

  new bootstrap.Modal(document.getElementById("editarEventoModal")).show();
}

function salvarEdicaoEvento() {
  var temEnsaios = document.getElementById("editTemEnsaiosExtras").checked;
  var ensaiosExtras = "Nenhum";

  if (temEnsaios) {
    var tipoSelecionado = document.querySelector(
      'input[name="editTipoEnsaio"]:checked',
    );
    if (tipoSelecionado) {
      if (tipoSelecionado.value === "Outros") {
        ensaiosExtras =
          document.getElementById("editOutrosEnsaioTexto").value || "Outros";
      } else {
        ensaiosExtras = tipoSelecionado.value;
      }
    }
  }

  var dados = {
    cliente: document.getElementById("editCliente").value,
    tipo_servico: document.getElementById("editTipoServico").value,
    data_evento: document.getElementById("editDataEvento").value,
    valor_negociado: parseFloat(
      document.getElementById("editValorNegociado").value,
    ),
    valor_pago: parseFloat(document.getElementById("editValorPago").value),
    status: document.getElementById("editStatus").value,
    ensaios_extras: ensaiosExtras,
    observacoes: document.getElementById("editObservacoes").value,
  };

  fetch("/evento/" + eventoIdEdicao + "/editar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      if (data.success) {
        bootstrap.Modal.getInstance(
          document.getElementById("editarEventoModal"),
        ).hide();
        location.reload();
      }
    })
    .catch(function () {
      alert("Erro ao salvar alterações. Tente novamente.");
    });
}

// ===== EXCLUIR EVENTO =====
function excluirEvento(eventoId, nomeCliente) {
  eventoIdExclusao = eventoId;
  document.getElementById("mensagemConfirmacao").innerHTML =
    'Deseja realmente excluir o evento do cliente <strong>"' +
    nomeCliente +
    '"</strong>?';

  var modal = new bootstrap.Modal(
    document.getElementById("confirmarExclusaoModal"),
  );
  modal.show();

  document.getElementById("btnConfirmarExclusao").onclick = function () {
    fetch("/evento/" + eventoIdExclusao + "/excluir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.success) {
          modal.hide();
          location.reload();
        }
      })
      .catch(function () {
        alert("Erro ao excluir evento. Tente novamente.");
      });
  };
}
