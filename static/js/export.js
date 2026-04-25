/**
 * export.js — Funções de exportação PDF/Excel para Photo Pro Studio.
 */

async function exportar(tipo, formato, btn) {
  // tipo: 'eventos' | 'caixa'
  // formato: 'excel' | 'pdf'
  if (!btn) btn = event.currentTarget;
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';

  try {
    let params = new URLSearchParams();

    if (tipo === "eventos") {
      const cliente = document.getElementById("filtroCliente");
      const servico = document.getElementById("filtroServico");
      const dataDe = document.getElementById("filtroDataDe");
      const dataAte = document.getElementById("filtroDataAte");
      const status = document.getElementById("filtroStatus");

      if (cliente && cliente.value) params.set("cliente", cliente.value);
      if (servico && servico.value) params.set("servico", servico.value);
      if (dataDe && dataDe.value) params.set("data_de", dataDe.value);
      if (dataAte && dataAte.value) params.set("data_ate", dataAte.value);
      if (status && status.value) params.set("status", status.value);
    }

    const url = `/exportar/${tipo}/${formato}?${params.toString()}`;
    const response = await fetch(url);

    if (!response.ok) {
      let msg = "Erro ao gerar exportação";
      try {
        const data = await response.json();
        msg = data.error || msg;
      } catch (_) {}
      alert(msg);
      return;
    }

    const blob = await response.blob();
    const contentDisposition =
      response.headers.get("Content-Disposition") || "";
    let filename = `${tipo}.${formato === "excel" ? "xlsx" : "pdf"}`;
    const match = contentDisposition.match(/filename=(.+)/);
    if (match) filename = match[1].replace(/"/g, "");

    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  } catch (e) {
    alert("Erro de conexão ao gerar exportação");
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}

async function gerarRelatorioMensal(btn) {
  if (!btn) btn = event.currentTarget;
  const mesInput = document.getElementById("mesRelatorio");
  if (!mesInput || !mesInput.value) {
    alert("Selecione o mês para gerar o relatório.");
    return;
  }

  const [ano, mes] = mesInput.value.split("-");
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';

  try {
    const url = `/exportar/relatorio-mensal?mes=${parseInt(mes)}&ano=${parseInt(ano)}`;
    const response = await fetch(url);

    if (!response.ok) {
      let msg = "Erro ao gerar relatório";
      try {
        const data = await response.json();
        msg = data.error || msg;
      } catch (_) {}
      alert(msg);
      return;
    }

    const blob = await response.blob();
    const contentDisposition =
      response.headers.get("Content-Disposition") || "";
    let filename = `relatorio_mensal_${ano}-${mes}.pdf`;
    const match = contentDisposition.match(/filename=(.+)/);
    if (match) filename = match[1].replace(/"/g, "");

    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  } catch (e) {
    alert("Erro de conexão ao gerar relatório");
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}
