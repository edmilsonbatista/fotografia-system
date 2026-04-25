# Implementation Plan: Export PDF/Excel

## Overview

Add PDF and Excel export capabilities to Photo Pro Studio. The implementation creates an `export_utils.py` module with pure functions for file generation (pandas/openpyxl for Excel, ReportLab for PDF), new Flask routes in `app.py`, a shared `export.js` frontend handler, and UI buttons on the Eventos and Caixa pages. All exports use Brazilian formatting (R$, dd/mm/yyyy) and PDF documents carry studio branding.

## Tasks

- [x] 1. Install dependencies and create export_utils.py with formatting helpers
  - Add `reportlab` to `requirements.txt`
  - Create `export_utils.py` at project root
  - Implement `format_brl(value)` — formats float as "R$ 1.234,56"
  - Implement `format_date_br(d)` — formats date as dd/mm/yyyy
  - Implement shared PDF helper `_add_branding_header(canvas, logo_path)` for the Photo Pro Studio logo and name
  - _Requirements: 1.3, 1.4, 2.2, 2.4, 2.5, 3.6, 3.7, 4.4, 4.5, 5.7, 5.8_

- [x] 2. Implement events export functions
  - [x] 2.1 Implement `gerar_excel_eventos(eventos, data_atual)` in `export_utils.py`
    - Generate .xlsx with columns: Cliente, Tipo de Serviço, Data do Evento, Ensaios Extras, Valor Negociado, Valor Pago, Status
    - Add summary row with totals for Valor Negociado and Valor Pago
    - Handle empty list: header + zero-total summary row only
    - Return BytesIO object
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [ ]\* 2.2 Write property test for events Excel data integrity
    - **Property 3: Events Excel data integrity**
    - **Validates: Requirements 1.1, 1.2, 1.5**

  - [x] 2.3 Implement `gerar_pdf_eventos(eventos, data_atual, logo_path)` in `export_utils.py`
    - Generate A4 landscape PDF with branding header
    - Render events as formatted table with columns: Cliente, Serviço, Data, Ensaios, Negociado, Pago, Status
    - Add summary row with totals
    - Handle empty list: branding header + "Nenhum evento encontrado para os filtros selecionados"
    - Return BytesIO object
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [x] 3. Implement cash flow export functions
  - [x] 3.1 Implement `gerar_excel_caixa(transacoes, pendentes, entradas, saidas, saldo, total_pendente, data_atual)` in `export_utils.py`
    - Main sheet "Transações" with columns: Data, Tipo, Descrição, Categoria, Valor
    - Summary rows: Total de Entradas, Total de Saídas, Saldo Atual
    - Separate "Pendentes" sheet with pending transactions and Total Pendente summary
    - Return BytesIO object
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]\* 3.2 Write property test for cash flow Excel data integrity
    - **Property 4: Cash flow Excel data integrity with multi-sheet structure**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.6**

  - [x] 3.3 Implement `gerar_pdf_caixa(transacoes, pendentes, entradas, saidas, saldo, data_atual, logo_path)` in `export_utils.py`
    - Branding header, transactions table with color-coded types (green for Entrada, red for Saída)
    - Summary section: Total de Entradas, Total de Saídas, Saldo Atual
    - Separate "Entradas Pendentes" section with columns: Data Prevista, Cliente, Valor Pendente
    - Handle empty: branding header + "Nenhuma transação encontrada"
    - Return BytesIO object
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9_

- [x] 4. Implement monthly financial report
  - [x] 4.1 Implement `gerar_pdf_relatorio_mensal(mes, ano, eventos, transacoes, resumo, logo_path)` in `export_utils.py`
    - Branding header + title "Relatório Financeiro Mensal - [Mês/Ano]" with Portuguese month name
    - Financial summary section: Total de Entradas, Total de Saídas, Saldo do Mês, Total Negociado, Total Recebido, Total Pendente
    - Events table: Cliente, Serviço, Data, Valor Negociado, Valor Pago, Status
    - Transactions table: Data, Tipo, Descrição, Categoria, Valor
    - Handle empty month: zero summary + "Nenhum registro encontrado para o período"
    - Return BytesIO object
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [ ]\* 4.2 Write property test for monthly report summary computation
    - **Property 5: Monthly report summary computation**
    - **Validates: Requirements 3.3**

- [x] 5. Checkpoint - Verify export_utils.py
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Add Flask export routes to app.py
  - [x] 6.1 Add events export routes
    - `GET /exportar/eventos/excel` — query Evento with filter params (cliente, servico, data_de, data_ate, status), call `gerar_excel_eventos`, return via `send_file` with correct headers and filename `eventos_YYYY-MM-DD.xlsx`
    - `GET /exportar/eventos/pdf` — same filters, call `gerar_pdf_eventos`, return with filename `eventos_YYYY-MM-DD.pdf`
    - Both routes: `@login_required`, try/except returning JSON error on failure, correct Content-Type and Content-Disposition headers
    - _Requirements: 1.1, 1.7, 2.1, 2.9, 7.1, 7.2, 7.3, 7.4, 7.6, 7.7_

  - [x] 6.2 Add cash flow export routes
    - `GET /exportar/caixa/excel` — query realized transactions + pending transactions (same logic as `caixa()` route), call `gerar_excel_caixa`, return with filename `caixa_YYYY-MM-DD.xlsx`
    - `GET /exportar/caixa/pdf` — same data, call `gerar_pdf_caixa`, return with filename `caixa_YYYY-MM-DD.pdf`
    - Both routes: `@login_required`, try/except, correct headers
    - _Requirements: 4.1, 4.7, 5.1, 5.10, 7.1, 7.3, 7.4, 7.6, 7.7_

  - [x] 6.3 Add monthly report route
    - `GET /exportar/relatorio-mensal?mes=MM&ano=YYYY` — query events and transactions for the month, compute summary dict, call `gerar_pdf_relatorio_mensal`, return with filename `relatorio_mensal_YYYY-MM.pdf`
    - Validate mes/ano params, return 400 on invalid input
    - `@login_required`, try/except, correct headers
    - _Requirements: 3.1, 3.10, 7.1, 7.3, 7.4, 7.5, 7.6, 7.7_

- [ ]\* 7. Write property tests for formatting and response headers
  - [ ]\* 7.1 Write property test for Brazilian currency formatting
    - **Property 1: Brazilian currency formatting round-trip**
    - **Validates: Requirements 1.3, 2.4, 3.6, 4.4, 5.7**

  - [ ]\* 7.2 Write property test for date formatting
    - **Property 2: Date formatting correctness**
    - **Validates: Requirements 1.4, 2.5, 3.7, 4.5, 5.8**

  - [ ]\* 7.3 Write property test for export filename patterns
    - **Property 6: Export filename pattern**
    - **Validates: Requirements 1.7, 2.9, 3.10, 4.7, 5.10**

  - [ ]\* 7.4 Write property test for export response headers
    - **Property 7: Export response headers**
    - **Validates: Requirements 7.6, 7.7**

- [x] 8. Create frontend export handler (static/js/export.js)
  - Implement `exportar(tipo, formato)` function that collects current filter values from DOM, builds export URL with query params, uses `fetch()` to request the file, handles errors (shows alert with JSON error message), triggers download via blob URL on success
  - Implement loading spinner on button + disable during generation, restore in `finally` block
  - Implement `gerarRelatorioMensal()` function that reads month/year selector values and triggers the monthly report download
  - _Requirements: 6.8, 7.3, 7.4_

- [x] 9. Add export UI buttons to templates
  - [x] 9.1 Update `templates/eventos.html`
    - Add "Exportar Excel" (green gradient, file-excel icon) and "Exportar PDF" (red gradient, file-pdf icon) buttons in the header area next to "Novo Evento"
    - Buttons call `exportar('eventos', 'excel')` and `exportar('eventos', 'pdf')`
    - Include `export.js` in the scripts block
    - _Requirements: 6.1, 6.4, 6.5, 6.6, 6.8_

  - [x] 9.2 Update `templates/caixa.html`
    - Add "Exportar Excel" (green gradient) and "Exportar PDF" (red gradient) buttons near "Nova Transação"
    - Add "Relatório Mensal" button (blue gradient, chart-bar icon) with month/year `<input type="month">` selector
    - Include `export.js` in the scripts block
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [ ]\* 10. Write unit and integration tests
  - [ ]\* 10.1 Write unit tests for empty data edge cases
    - Empty events → Excel with header + zero summary (Req 1.6)
    - Empty events → PDF with "Nenhum evento encontrado" message (Req 2.8)
    - Empty month → PDF with zero summary and "Nenhum registro" message (Req 3.9)
    - Empty transactions → PDF with "Nenhuma transação encontrada" (Req 5.9)
    - _Requirements: 1.6, 2.8, 3.9, 5.9_

  - [ ]\* 10.2 Write integration tests for authentication and error handling
    - All 5 export endpoints require authentication (redirect to login)
    - Successful download returns correct Content-Type and Content-Disposition
    - Error responses return HTTP 500 with JSON error message
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [ ] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis (Python) as specified in the design
- `export_utils.py` uses pure functions with BytesIO returns — no temp files on disk
- ReportLab is used for PDF (pure Python, no system dependencies)
- pandas + openpyxl (already installed) handle Excel generation
