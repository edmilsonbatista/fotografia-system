# Requirements Document

## Introduction

This feature adds PDF and Excel export capabilities to the Photo Pro Studio photography management system. Users will be able to export events tables, cash flow transactions, and monthly financial reports as downloadable files. All exports respect currently applied filters, use Brazilian formatting (R$ currency, dd/mm/yyyy dates), require authentication, and carry Photo Pro Studio branding on PDF documents.

## Glossary

- **Export_Engine**: The backend module responsible for generating Excel (.xlsx) and PDF file outputs from queried data
- **Events_Table**: The list of Evento records displayed on the Eventos page, with columns: Cliente, Serviço, Data, Ensaios, Negociado, Pago, Status
- **Cash_Flow_Table**: The list of Transacao records (type Entrada or Saída) displayed on the Caixa page
- **Pending_Table**: The list of Transacao records with type "Entrada Pendente" displayed in the Caixa page's pending section
- **Monthly_Report**: A PDF document summarizing financial data for a selected month, including totals, event listings, and chart-ready data
- **Filter_Parameters**: The set of active filter values (cliente, serviço, data_de, data_ate, status) applied by the user on the Eventos or Caixa pages
- **Brazilian_Format**: Number formatting using comma as decimal separator, period as thousands separator, R$ currency prefix, and dd/mm/yyyy date format
- **Branding_Header**: A PDF header section containing the Photo Pro Studio logo (static/img/photoprostudio.png) and studio name
- **Authenticated_User**: A user who has successfully logged in via Flask-Login and has an active session

## Requirements

### Requirement 1: Export Events to Excel

**User Story:** As a studio manager, I want to export the events table to an Excel file, so that I can analyze event data in spreadsheets and share it with partners.

#### Acceptance Criteria

1. WHEN the Authenticated_User clicks the "Exportar Excel" button on the Eventos page, THE Export_Engine SHALL generate an Excel (.xlsx) file containing the currently visible (filtered) events
2. THE Export_Engine SHALL include the following columns in the Excel output: Cliente, Tipo de Serviço, Data do Evento, Ensaios Extras, Valor Negociado, Valor Pago, Status
3. THE Export_Engine SHALL format all monetary values in Brazilian_Format in the Excel output
4. THE Export_Engine SHALL format all dates in dd/mm/yyyy format in the Excel output
5. THE Export_Engine SHALL include a summary row at the bottom of the Excel file with totals for Valor Negociado and Valor Pago
6. WHEN no events match the current Filter_Parameters, THE Export_Engine SHALL return an Excel file with only the header row and summary row showing zero totals
7. THE Export_Engine SHALL name the downloaded file using the pattern "eventos_YYYY-MM-DD.xlsx" where the date is the current date

### Requirement 2: Export Events to PDF

**User Story:** As a studio manager, I want to export the events table to a PDF file, so that I can print or email a formatted report of my events.

#### Acceptance Criteria

1. WHEN the Authenticated_User clicks the "Exportar PDF" button on the Eventos page, THE Export_Engine SHALL generate a PDF file containing the currently visible (filtered) events
2. THE Export_Engine SHALL include a Branding_Header at the top of the PDF document with the Photo Pro Studio logo and name
3. THE Export_Engine SHALL render the events as a formatted table in the PDF with columns: Cliente, Serviço, Data, Ensaios, Negociado, Pago, Status
4. THE Export_Engine SHALL format all monetary values in Brazilian_Format in the PDF output
5. THE Export_Engine SHALL format all dates in dd/mm/yyyy format in the PDF output
6. THE Export_Engine SHALL include a summary row at the bottom of the PDF table with totals for Valor Negociado and Valor Pago
7. THE Export_Engine SHALL use A4 landscape orientation for the PDF to accommodate the table width
8. WHEN no events match the current Filter_Parameters, THE Export_Engine SHALL generate a PDF with the Branding_Header and a message stating "Nenhum evento encontrado para os filtros selecionados"
9. THE Export_Engine SHALL name the downloaded file using the pattern "eventos_YYYY-MM-DD.pdf" where the date is the current date

### Requirement 3: Monthly Financial Report as PDF

**User Story:** As a studio manager, I want to generate a monthly financial report as a PDF, so that I can review the studio's financial performance for any given month.

#### Acceptance Criteria

1. WHEN the Authenticated_User selects a month/year and clicks "Gerar Relatório" on the Dashboard or Caixa page, THE Export_Engine SHALL generate a PDF monthly financial report
2. THE Export_Engine SHALL include a Branding_Header at the top of the monthly report PDF
3. THE Export_Engine SHALL include a financial summary section with: Total de Entradas, Total de Saídas, Saldo do Mês, Total Negociado, Total Recebido, Total Pendente
4. THE Export_Engine SHALL include a list of all events for the selected month with columns: Cliente, Serviço, Data, Valor Negociado, Valor Pago, Status
5. THE Export_Engine SHALL include a list of all transactions (Entrada and Saída) for the selected month with columns: Data, Tipo, Descrição, Categoria, Valor
6. THE Export_Engine SHALL format all monetary values in Brazilian_Format in the monthly report
7. THE Export_Engine SHALL format all dates in dd/mm/yyyy format in the monthly report
8. THE Export_Engine SHALL display the report title as "Relatório Financeiro Mensal - [Mês/Ano]" where Mês is the month name in Portuguese
9. WHEN no events or transactions exist for the selected month, THE Export_Engine SHALL generate the PDF with the summary section showing zero values and empty tables with a message "Nenhum registro encontrado para o período"
10. THE Export_Engine SHALL name the downloaded file using the pattern "relatorio_mensal_YYYY-MM.pdf"

### Requirement 4: Export Cash Flow Transactions to Excel

**User Story:** As a studio manager, I want to export cash flow transactions to an Excel file, so that I can perform detailed financial analysis in spreadsheets.

#### Acceptance Criteria

1. WHEN the Authenticated_User clicks the "Exportar Excel" button on the Caixa page, THE Export_Engine SHALL generate an Excel (.xlsx) file containing the realized transactions (Entrada and Saída)
2. THE Export_Engine SHALL include the following columns in the Excel output: Data, Tipo, Descrição, Categoria, Valor
3. THE Export_Engine SHALL include a separate sheet named "Pendentes" containing the pending transactions (Entrada Pendente) from non-cancelled events
4. THE Export_Engine SHALL format all monetary values in Brazilian_Format in the Excel output
5. THE Export_Engine SHALL format all dates in dd/mm/yyyy format in the Excel output
6. THE Export_Engine SHALL include summary rows with: Total de Entradas, Total de Saídas, Saldo Atual on the main sheet, and Total Pendente on the Pendentes sheet
7. THE Export_Engine SHALL name the downloaded file using the pattern "caixa_YYYY-MM-DD.xlsx" where the date is the current date

### Requirement 5: Export Cash Flow Transactions to PDF

**User Story:** As a studio manager, I want to export cash flow transactions to a PDF file, so that I can print or archive a formatted record of financial movements.

#### Acceptance Criteria

1. WHEN the Authenticated_User clicks the "Exportar PDF" button on the Caixa page, THE Export_Engine SHALL generate a PDF file containing the realized transactions (Entrada and Saída)
2. THE Export_Engine SHALL include a Branding_Header at the top of the PDF document
3. THE Export_Engine SHALL render the transactions as a formatted table with columns: Data, Tipo, Descrição, Categoria, Valor
4. THE Export_Engine SHALL color-code transaction types in the PDF: green text for "Entrada" and red text for "Saída"
5. THE Export_Engine SHALL include a summary section at the bottom with: Total de Entradas, Total de Saídas, Saldo Atual
6. THE Export_Engine SHALL include a separate section for pending transactions titled "Entradas Pendentes" with columns: Data Prevista, Cliente, Valor Pendente
7. THE Export_Engine SHALL format all monetary values in Brazilian_Format in the PDF output
8. THE Export_Engine SHALL format all dates in dd/mm/yyyy format in the PDF output
9. WHEN no transactions exist, THE Export_Engine SHALL generate a PDF with the Branding_Header and a message stating "Nenhuma transação encontrada"
10. THE Export_Engine SHALL name the downloaded file using the pattern "caixa_YYYY-MM-DD.pdf" where the date is the current date

### Requirement 6: Export UI Buttons

**User Story:** As a studio manager, I want clearly visible export buttons on the relevant pages, so that I can easily trigger exports without navigating away from my current view.

#### Acceptance Criteria

1. THE Eventos page SHALL display "Exportar Excel" and "Exportar PDF" buttons in the page header area, next to the existing "Novo Evento" button
2. THE Caixa page SHALL display "Exportar Excel" and "Exportar PDF" buttons near the "Nova Transação" button area
3. THE Dashboard or Caixa page SHALL display a "Relatório Mensal" button with a month/year selector for generating the monthly financial report
4. THE export buttons SHALL use gradient styling consistent with the existing Photo Pro Studio UI (linear-gradient backgrounds with white text and Font Awesome icons)
5. THE "Exportar Excel" buttons SHALL use a green gradient style with a file-excel icon
6. THE "Exportar PDF" buttons SHALL use a red gradient style with a file-pdf icon
7. THE "Relatório Mensal" buttons SHALL use a blue gradient style with a chart-bar icon
8. WHILE an export is being generated, THE export button SHALL display a loading spinner and become disabled to prevent duplicate requests

### Requirement 7: Authentication and Error Handling for Exports

**User Story:** As a studio manager, I want export endpoints to be secure and handle errors gracefully, so that only authorized users can generate exports and failures are communicated clearly.

#### Acceptance Criteria

1. THE Export_Engine SHALL require authentication (@login_required) for all export endpoints
2. IF an unauthenticated request is made to an export endpoint, THEN THE Export_Engine SHALL redirect the user to the login page
3. IF an error occurs during Excel file generation, THEN THE Export_Engine SHALL return an HTTP 500 response with a JSON error message describing the failure
4. IF an error occurs during PDF file generation, THEN THE Export_Engine SHALL return an HTTP 500 response with a JSON error message describing the failure
5. IF the PDF generation library (ReportLab or WeasyPrint) is not installed, THEN THE Export_Engine SHALL return an HTTP 500 response with a message indicating the missing dependency
6. THE Export_Engine SHALL set the correct Content-Type header: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" for Excel and "application/pdf" for PDF
7. THE Export_Engine SHALL set the Content-Disposition header to "attachment" with the appropriate filename for all export responses
