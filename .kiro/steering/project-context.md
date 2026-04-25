# Photo Pro Studio - Sistema de Gestão para Fotografia

## Sobre o Projeto

Sistema web de gestão financeira e de eventos para um estúdio de fotografia e storymaker (vídeo). Desenvolvido em Python/Flask com SQLite, interface Bootstrap 5 com design moderno usando gradientes e animações.

## Stack Técnica

- Backend: Flask 2.3.3 + Flask-SQLAlchemy 3.0.5
- Banco: SQLite (instance/fotografia.db)
- Frontend: Bootstrap 5.3.2, Font Awesome 6.5.1, Chart.js 3.9.1
- Importação: pandas + openpyxl para Excel/CSV
- Servidor: python app.py (porta 5000, debug mode)

## Estrutura do Projeto

```
app.py              # Backend principal (rotas, modelos, APIs)
templates/
  base.html         # Layout base (navbar, Bootstrap, Chart.js)
  dashboard.html    # Dashboard com cards, gráficos, calendário
  eventos.html      # Lista de eventos com filtros
  novo_evento.html  # Formulário de cadastro de evento
  caixa.html        # Controle financeiro (entradas/saídas/pendentes)
  importar.html     # Importação de dados Excel/CSV
static/
  css/style.css     # Estilos customizados (gradientes, animações)
  js/eventos.js     # JS da página de eventos (filtros, CRUD)
  js/caixa.js       # JS da página de caixa (edição, exclusão)
  img/              # Logo e imagens do sistema
instance/
  fotografia.db     # Banco SQLite
```

## Modelos de Dados

### Evento

- id, cliente, tipo_servico (Fotografia/Storymaker/Fotografia + Storymaker)
- data_evento (Date), valor_negociado (Float), valor_pago (Float)
- status (Agendado/Realizado/Cancelado/Pendente)
- ensaios_extras, observacoes, data_cadastro
- Relacionamento CASCADE com Transacao

### Transacao

- id, evento_id (FK nullable), tipo (Entrada/Saída/Entrada Pendente)
- valor, descricao, data_transacao, categoria

## Regras de Negócio Importantes

- Ao criar evento: gera automaticamente uma Transacao "Entrada Pendente"
- Ao pagar evento: cria Transacao "Entrada" e atualiza/remove a pendente
- Ao reverter pagamento: restaura a pendente com saldo correto
- Eventos cancelados: botão Pagar fica desabilitado (cinza)
- Pendentes de eventos cancelados NÃO aparecem no caixa
- Saldo do caixa = Entradas - Saídas (pendentes não contam)
- Evento vira "Realizado" automaticamente quando valor_pago >= valor_negociado

## Padrões de UI/UX

- Layout centralizado: `row justify-content-center` > `col-md-10 col-lg-8`
- Cards de resumo em full-width com gradientes (bg-primary, bg-success, etc.)
- Cards secundários com `border-start border-4 shadow-sm`
- Tabelas com `table-striped` dentro de cards com header
- Badges coloridos para status e tipos de serviço
- Modais para edição, detalhes, exclusão e pagamento
- Botões de ação compactos (só ícones) nas tabelas
- Animações CSS: hover-lift, slideIn, transições suaves

## Padrões de Código

- JS em arquivos separados (static/js/) para evitar conflito com Jinja ($)
- Filtros Jinja seguros: |moeda, |numero, |data, |datahora (tratam None/tipos inválidos)
- APIs REST retornam JSON com try/except por item (um registro ruim não derruba tudo)
- Formatação brasileira: R$ com vírgula decimal, datas dd/mm/yyyy
- Datas no banco sempre em formato ISO yyyy-mm-dd

## Gráficos (Chart.js)

- Receita por Mês: combo bar+line com 3 visões (Planejado/Real/Recebido)
- Serviços por Tipo: doughnut clicável que abre lista de eventos ao lado
- Calendário customizado em grid CSS com pontos coloridos por status

## Idioma

- Interface 100% em português brasileiro
- Comunicação com o desenvolvedor em português
