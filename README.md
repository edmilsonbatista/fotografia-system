# Sistema de Gestão para Fotografia e Storymaker

Um sistema web completo para gerenciar seu negócio de fotografia e produção de vídeos, com controle de caixa e dashboard visual.

## 🚀 Funcionalidades

### 📊 Dashboard Completo

- Visão geral dos negócios com gráficos interativos
- Estatísticas de receita e eventos
- Próximos eventos agendados
- Ações rápidas para cadastros

### 📅 Gestão de Eventos

- Cadastro de eventos de fotografia e storymaker
- Controle de status (Agendado, Realizado, Cancelado)
- Registro de pagamentos parciais e totais
- Histórico completo de eventos

### 💰 Controle de Caixa

- Registro de entradas e saídas
- Categorização de transações
- Saldo atual em tempo real
- Relatórios financeiros

### 📈 Relatórios Visuais

- Gráfico de receita por mês
- Distribuição de serviços por tipo
- Análise de performance do negócio

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask + SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Gráficos**: Chart.js
- **Banco de Dados**: SQLite
- **Ícones**: Font Awesome

## 📋 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone ou baixe o projeto**

   ```bash
   cd fotografia-sistema
   ```

2. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**

   ```bash
   python app.py
   ```

4. **Acesse o sistema**
   - Abra seu navegador
   - Vá para: `http://localhost:4000`

## 📖 Como Usar

### 1. Dashboard

- Acesse a página inicial para ver o resumo do seu negócio
- Visualize gráficos de receita e distribuição de serviços
- Veja os próximos eventos agendados

### 2. Cadastrar Eventos

- Clique em "Novo Evento" no dashboard ou na página de eventos
- Preencha os dados do cliente e evento
- Defina o valor negociado
- Adicione observações se necessário

### 3. Gerenciar Pagamentos

- Na lista de eventos, clique em "Pagar" para registrar pagamentos
- O sistema controla pagamentos parciais automaticamente
- Status do evento é atualizado conforme os pagamentos

### 4. Controle de Caixa

- Registre todas as entradas (pagamentos de clientes)
- Registre todas as saídas (equipamentos, transporte, etc.)
- Categorize as transações para melhor controle
- Acompanhe o saldo em tempo real

## 💡 Dicas de Uso

### Precificação Sugerida

- **Fotografia**: R$ 200-2000 (dependendo do tipo)
- **Storymaker**: R$ 300-3000 (dependendo da complexidade)
- **Pacote Completo**: Desconto de 10-20%

### Categorias de Gastos

- **Equipamento**: Câmeras, lentes, iluminação
- **Transporte**: Combustível, pedágios
- **Marketing**: Anúncios, materiais promocionais
- **Manutenção**: Reparos, limpeza de equipamentos

### Organização

- Cadastre eventos assim que fechados
- Registre pagamentos imediatamente
- Mantenha o caixa sempre atualizado
- Revise o dashboard semanalmente

## 🔒 Segurança

- Altere a `SECRET_KEY` no arquivo `app.py` antes de usar em produção
- Faça backup regular do arquivo `fotografia.db`
- Mantenha o sistema atualizado

## 🗄️ Acesso Manual ao Banco de Dados

### Método 1 - Script Python (Recomendado)

```bash
python acesso_banco.py
```

### Método 2 - SQLite Command Line

```bash
acessar_sqlite.bat
```

### Método 3 - DB Browser (Interface Gráfica)

1. Baixe: https://sqlitebrowser.org/
2. Abra o arquivo: `instance/fotografia.db`
3. Use a interface gráfica para visualizar/editar

### Comandos SQL Úteis

```sql
-- Listar todos os eventos
SELECT * FROM evento;

-- Inserir evento manualmente
INSERT INTO evento (cliente, tipo_servico, data_evento, valor_negociado, valor_pago, status, observacoes, data_cadastro)
VALUES ('João Silva', 'Fotografia', '2024-03-15', 800.00, 400.00, 'Agendado', 'Casamento', datetime('now'));

-- Inserir transação manualmente
INSERT INTO transacao (tipo, valor, descricao, data_transacao, categoria)
VALUES ('Entrada', 400.00, 'Sinal do casamento', '2024-02-10', 'Pagamento de Cliente');

-- Ver estatísticas
SELECT status, COUNT(*) FROM evento GROUP BY status;
SELECT tipo, SUM(valor) FROM transacao GROUP BY tipo;
```

### ⚠️ Cuidados Importantes

- **Sempre faça backup** do arquivo `instance/fotografia.db` antes de modificações
- **Não altere IDs** manualmente para evitar conflitos
- **Use formato de data** 'YYYY-MM-DD' (ex: 2024-03-15)
- **Valores decimais** devem usar ponto (.) como separador (ex: 800.00)

## 📁 Estrutura do Projeto

```
fotografia-sistema/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências Python
├── fotografia.db         # Banco de dados (criado automaticamente)
├── templates/            # Templates HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── eventos.html
│   ├── novo_evento.html
│   └── caixa.html
└── static/              # Arquivos estáticos
    └── css/
        └── style.css
```

## 🆘 Suporte

Se encontrar algum problema:

1. Verifique se todas as dependências estão instaladas
2. Certifique-se de que a porta 4000 está disponível
3. Verifique se o Python está na versão correta

## 📝 Licença

Este projeto é de uso livre para fins pessoais e comerciais.

---

**Desenvolvido para fotógrafos e videomakers que querem profissionalizar seu negócio! 📸🎬**
