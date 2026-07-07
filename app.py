from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os
import click
import pandas as pd
from werkzeug.utils import secure_filename
import export_utils

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fotografia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Filtro personalizado para formatação brasileira
@app.template_filter('moeda')
def moeda_filter(valor):
    """Formata valor como moeda brasileira"""
    try:
        valor = float(valor) if valor else 0
    except (ValueError, TypeError):
        valor = 0
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

@app.template_filter('numero')
def numero_filter(valor):
    """Formata número com separador de milhares brasileiro"""
    try:
        valor = float(valor) if valor else 0
    except (ValueError, TypeError):
        valor = 0
    return f"{valor:,.0f}".replace(',', '.')

@app.template_filter('data')
def data_filter(valor, formato='%d/%m/%Y'):
    """Formata data de forma segura"""
    if valor is None:
        return '-'
    try:
        return valor.strftime(formato)
    except (AttributeError, ValueError):
        return str(valor)

@app.template_filter('datahora')
def datahora_filter(valor, formato='%d/%m/%Y %H:%M'):
    """Formata datetime de forma segura"""
    if valor is None:
        return '-'
    try:
        return valor.strftime(formato)
    except (AttributeError, ValueError):
        return str(valor)

# Criar pasta de uploads se não existir
if not os.path.exists('uploads'):
    os.makedirs('uploads')

db = SQLAlchemy(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar o sistema.'
login_manager.login_message_category = 'info'

# Modelo de usuário
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Modelos do banco de dados
class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    tipo_servico = db.Column(db.String(50), nullable=False)  # Fotografia, Storymaker, Ambos
    data_evento = db.Column(db.Date, nullable=False)
    valor_negociado = db.Column(db.Float, nullable=False)
    valor_pago = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Agendado')  # Agendado, Realizado, Cancelado
    observacoes = db.Column(db.Text)
    ensaios_extras = db.Column(db.String(100), nullable=False, default='Nenhum')
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com transações (CASCADE delete)
    transacoes = db.relationship('Transacao', backref='evento', lazy=True, cascade='all, delete-orphan')

class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id', ondelete='CASCADE'))
    tipo = db.Column(db.String(20), nullable=False)  # Entrada, Saída, Entrada Pendente
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    data_transacao = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(50))  # Equipamento, Transporte, etc.

# CLI command para criar admin
@app.cli.command('create-admin')
@click.option('--username', prompt=True, help='Nome do usuário admin')
@click.option('--password', prompt=True, hide_input=True, help='Senha do admin')
def create_admin(username, password):
    """Cria um usuário administrador."""
    if Usuario.query.filter_by(username=username).first():
        click.echo('Usuário já existe!')
        return
    user = Usuario(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo('Usuário admin criado com sucesso!')

# Custom unauthorized handler
@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Autenticação necessária.'}), 401
    flash('Por favor, faça login para acessar o sistema.', 'info')
    return redirect(url_for('login', next=request.url))

# Rotas
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        try:
            user = Usuario.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            flash('Usuário ou senha inválidos.', 'danger')
        except Exception:
            flash('Erro ao processar login. Tente novamente.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/usuarios')
@login_required
def listar_usuarios():
    if not current_user.is_admin:
        flash('Apenas o administrador pode gerenciar usuários.', 'danger')
        return redirect(url_for('dashboard'))
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuario/novo', methods=['POST'])
@login_required
def novo_usuario():
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Sem permissão'}), 403
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    if not username or not password:
        flash('Usuário e senha são obrigatórios.', 'danger')
        return redirect(url_for('listar_usuarios'))
    if Usuario.query.filter_by(username=username).first():
        flash(f'Usuário "{username}" já existe!', 'danger')
        return redirect(url_for('listar_usuarios'))
    is_admin = request.form.get('is_admin') == 'on'
    user = Usuario(username=username, is_admin=is_admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f'Usuário "{username}" criado com sucesso!', 'success')
    return redirect(url_for('listar_usuarios'))

@app.route('/usuario/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_usuario(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Sem permissão'}), 403
    user = Usuario.query.get_or_404(id)
    if user.username == 'admin':
        return jsonify({'success': False, 'error': 'Não é possível excluir o admin.'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/usuario/<int:id>/alterar-senha', methods=['POST'])
@login_required
def alterar_senha_usuario(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Sem permissão'}), 403
    user = Usuario.query.get_or_404(id)
    data = request.get_json()
    nova_senha = data.get('password', '')
    if not nova_senha:
        return jsonify({'success': False, 'error': 'Senha não pode ser vazia.'}), 400
    user.set_password(nova_senha)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/')
@login_required
def dashboard():
    hoje = date.today()
    
    # Estatísticas básicas
    total_eventos = Evento.query.count()
    
    # Eventos do mês atual (apenas agendados e realizados)
    eventos_mes = Evento.query.filter(
        db.func.strftime('%Y-%m', Evento.data_evento) == hoje.strftime('%Y-%m'),
        Evento.status.in_(['Agendado', 'Realizado'])
    ).count()
    
    # Receitas (baseadas em valor_pago - dinheiro realmente recebido)
    receita_total = db.session.query(db.func.sum(Evento.valor_pago)).scalar() or 0
    
    # Receita do mês (apenas eventos realizados ou com pagamento)
    receita_mes = db.session.query(db.func.sum(Evento.valor_pago)).filter(
        db.func.strftime('%Y-%m', Evento.data_evento) == hoje.strftime('%Y-%m'),
        Evento.valor_pago > 0
    ).scalar() or 0
    
    # Previsão de receita do mês (valor negociado de eventos agendados e pendentes)
    previsao_mes = db.session.query(db.func.sum(Evento.valor_negociado)).filter(
        db.func.strftime('%Y-%m', Evento.data_evento) == hoje.strftime('%Y-%m'),
        Evento.status.in_(['Agendado', 'Pendente'])
    ).scalar() or 0
    
    # Status dos eventos (todos os eventos, independente da data)
    eventos_agendados = Evento.query.filter_by(status='Agendado').count()
    eventos_realizados = Evento.query.filter_by(status='Realizado').count()
    eventos_cancelados = Evento.query.filter_by(status='Cancelado').count()
    eventos_pendentes = Evento.query.filter_by(status='Pendente').count()
    
    # Valores financeiros totais (excluir eventos cancelados)
    todos_eventos = Evento.query.filter(Evento.status != 'Cancelado').all()
    total_negociado = sum(e.valor_negociado for e in todos_eventos)
    total_recebido = sum(e.valor_pago for e in todos_eventos)
    total_pendente = total_negociado - total_recebido
    
    # Eventos do mês vigente (todos os status)
    proximos_eventos = Evento.query.filter(
        db.func.strftime('%Y-%m', Evento.data_evento) == hoje.strftime('%Y-%m')
    ).order_by(Evento.data_evento.asc()).all()
    
    # Todos os eventos para o calendário
    todos_eventos_calendario = Evento.query.all()
    
    return render_template('dashboard.html',
                         total_eventos=total_eventos,
                         eventos_mes=eventos_mes,
                         receita_total=receita_total,
                         receita_mes=receita_mes,
                         previsao_mes=previsao_mes,
                         eventos_agendados=eventos_agendados,
                         eventos_realizados=eventos_realizados,
                         eventos_cancelados=eventos_cancelados,
                         eventos_pendentes=eventos_pendentes,
                         total_negociado=total_negociado,
                         total_recebido=total_recebido,
                         total_pendente=total_pendente,
                         proximos_eventos=proximos_eventos,
                         eventos=todos_eventos_calendario)

@app.route('/eventos')
@login_required
def listar_eventos():
    eventos = Evento.query.order_by(Evento.data_evento.asc()).all()
    
    # Estatísticas para os cards
    total = len(eventos)
    agendados = sum(1 for e in eventos if e.status == 'Agendado')
    realizados = sum(1 for e in eventos if e.status == 'Realizado')
    cancelados = sum(1 for e in eventos if e.status == 'Cancelado')
    total_negociado = sum(e.valor_negociado for e in eventos if e.status != 'Cancelado')
    total_recebido = sum(e.valor_pago for e in eventos if e.status != 'Cancelado')
    
    return render_template('eventos.html', eventos=eventos,
                         total=total, agendados=agendados,
                         realizados=realizados, cancelados=cancelados,
                         total_negociado=total_negociado,
                         total_recebido=total_recebido)

@app.route('/evento/novo', methods=['GET', 'POST'])
@login_required
def novo_evento():
    if request.method == 'POST':
        # Processar ensaios extras
        tem_ensaios = request.form.get('tem_ensaios_extras') == 'on'
        if tem_ensaios:
            tipo_ensaio = request.form.get('tipo_ensaio')
            if tipo_ensaio == 'Outros':
                ensaios_extras = request.form.get('outros_ensaio_texto', 'Outros')
            else:
                ensaios_extras = tipo_ensaio or 'Nenhum'
        else:
            ensaios_extras = 'Nenhum'
        
        evento = Evento(
            cliente=request.form['cliente'],
            tipo_servico=request.form['tipo_servico'],
            data_evento=datetime.strptime(request.form['data_evento'], '%Y-%m-%d').date(),
            valor_negociado=float(request.form['valor_negociado']),
            observacoes=request.form.get('observacoes', ''),
            ensaios_extras=ensaios_extras
        )
        db.session.add(evento)
        db.session.flush()  # Garante que o evento.id seja gerado
        
        # Criar transação pendente automaticamente
        transacao_pendente = Transacao(
            evento_id=evento.id,
            tipo='Entrada Pendente',
            valor=float(request.form['valor_negociado']),
            descricao=f'Saldo restante - {request.form["cliente"]}',
            data_transacao=datetime.strptime(request.form['data_evento'], '%Y-%m-%d').date(),
            categoria='Pagamento de Cliente'
        )
        db.session.add(transacao_pendente)
        
        db.session.commit()
        return redirect(url_for('listar_eventos'))
    
    return render_template('novo_evento.html')

@app.route('/api/verificar-data-evento')
@login_required
def verificar_data_evento():
    """Verifica se já existe evento na data especificada"""
    data = request.args.get('data')
    if not data:
        return jsonify({'existe': False})
    
    try:
        data_evento = datetime.strptime(data, '%Y-%m-%d').date()
        eventos = Evento.query.filter(
            Evento.data_evento == data_evento,
            Evento.status.in_(['Agendado', 'Pendente'])
        ).all()
        
        if eventos:
            eventos_info = [{
                'id': e.id,
                'cliente': e.cliente,
                'tipo_servico': e.tipo_servico,
                'valor': float(e.valor_negociado)
            } for e in eventos]
            
            return jsonify({
                'existe': True,
                'quantidade': len(eventos),
                'eventos': eventos_info
            })
        
        return jsonify({'existe': False})
    except:
        return jsonify({'existe': False})

@app.route('/evento/<int:id>/pagar', methods=['POST'])
@login_required
def registrar_pagamento(id):
    try:
        data = request.get_json()
        valor = float(data['valor'])
        
        evento = Evento.query.get_or_404(id)
        evento.valor_pago += valor
        
        # Criar transação de entrada no caixa
        transacao = Transacao(
            evento_id=id,
            tipo='Entrada',
            valor=valor,
            descricao=f'Pagamento - {evento.cliente}',
            data_transacao=date.today(),
            categoria='Pagamento de Cliente'
        )
        db.session.add(transacao)
        
        # Atualizar ou remover transação pendente correspondente
        pendente = Transacao.query.filter_by(
            evento_id=id,
            tipo='Entrada Pendente'
        ).first()
        
        if pendente:
            saldo_restante = evento.valor_negociado - evento.valor_pago
            if saldo_restante <= 0:
                # Pago totalmente — remover pendente
                db.session.delete(pendente)
            else:
                # Atualizar valor pendente com o saldo restante
                pendente.valor = saldo_restante
                pendente.descricao = f'Saldo restante - {evento.cliente}'
        
        if evento.valor_pago >= evento.valor_negociado:
            evento.status = 'Realizado'
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Erro no pagamento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/caixa')
@login_required
def caixa():
    # Buscar transações realizadas (Entrada e Saída) ordenadas por data
    transacoes_realizadas = Transacao.query.filter(
        Transacao.tipo.in_(['Entrada', 'Saída'])
    ).order_by(Transacao.data_transacao.desc()).all()
    
    # Buscar pendentes apenas de eventos NÃO cancelados
    transacoes_pendentes = db.session.query(Transacao).join(
        Evento, Transacao.evento_id == Evento.id
    ).filter(
        Transacao.tipo == 'Entrada Pendente',
        Evento.status.notin_(['Cancelado']),
        Evento.valor_pago < Evento.valor_negociado
    ).order_by(Transacao.data_transacao.asc()).all()
    
    # Calcular saldos
    entradas = db.session.query(db.func.sum(Transacao.valor)).filter(Transacao.tipo == 'Entrada').scalar() or 0
    saidas = db.session.query(db.func.sum(Transacao.valor)).filter(Transacao.tipo == 'Saída').scalar() or 0
    pendentes_total = sum(t.valor for t in transacoes_pendentes)
    
    saldo_atual = entradas - saidas
    saldo_projetado = saldo_atual + pendentes_total
    
    return render_template('caixa.html', 
                         transacoes=transacoes_realizadas,
                         transacoes_pendentes=transacoes_pendentes,
                         saldo=saldo_atual,
                         entradas=entradas,
                         saidas=saidas,
                         saldo_projetado=saldo_projetado,
                         total_pendente=pendentes_total)

@app.route('/transacao/nova', methods=['POST'])
@login_required
def nova_transacao():
    transacao = Transacao(
        tipo=request.form['tipo'],
        valor=float(request.form['valor']),
        descricao=request.form['descricao'],
        data_transacao=datetime.strptime(request.form['data_transacao'], '%Y-%m-%d').date(),
        categoria=request.form.get('categoria', '')
    )
    db.session.add(transacao)
    db.session.commit()
    return redirect(url_for('caixa'))

@app.route('/evento/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_evento(id):
    try:
        evento = Evento.query.get_or_404(id)
        
        # Excluir todas as transações relacionadas ao evento
        transacoes_relacionadas = Transacao.query.filter_by(evento_id=id).all()
        
        for transacao in transacoes_relacionadas:
            db.session.delete(transacao)
        
        # Excluir o evento
        db.session.delete(evento)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Evento e {len(transacoes_relacionadas)} transação(ões) excluídos'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/evento/<int:id>/editar', methods=['POST'])
@login_required
def editar_evento(id):
    evento = Evento.query.get_or_404(id)
    
    # Processar ensaios extras
    ensaios_extras = request.json.get('ensaios_extras', 'Nenhum')
    
    evento.cliente = request.json.get('cliente', evento.cliente)
    evento.tipo_servico = request.json.get('tipo_servico', evento.tipo_servico)
    evento.data_evento = datetime.strptime(request.json.get('data_evento'), '%Y-%m-%d').date() if request.json.get('data_evento') else evento.data_evento
    evento.valor_negociado = float(request.json.get('valor_negociado', evento.valor_negociado))
    evento.valor_pago = float(request.json.get('valor_pago', evento.valor_pago))
    evento.status = request.json.get('status', evento.status)
    evento.ensaios_extras = ensaios_extras
    evento.observacoes = request.json.get('observacoes', evento.observacoes)
    
    # Atualizar transação pendente
    saldo_restante = evento.valor_negociado - evento.valor_pago
    pendente = Transacao.query.filter_by(evento_id=id, tipo='Entrada Pendente').first()
    
    if evento.status == 'Cancelado' or saldo_restante <= 0:
        if pendente:
            db.session.delete(pendente)
    elif saldo_restante > 0:
        if pendente:
            pendente.valor = saldo_restante
            pendente.descricao = f'Saldo restante - {evento.cliente}'
            pendente.data_transacao = evento.data_evento
        else:
            nova = Transacao(
                evento_id=id, tipo='Entrada Pendente', valor=saldo_restante,
                descricao=f'Saldo restante - {evento.cliente}',
                data_transacao=evento.data_evento, categoria='Pagamento de Cliente'
            )
            db.session.add(nova)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/transacao/<int:id>/reverter', methods=['POST'])
@login_required
def reverter_pagamento(id):
    try:
        transacao = Transacao.query.get_or_404(id)
        
        # Só permite reverter transações de entrada com evento vinculado
        if transacao.tipo != 'Entrada' or not transacao.evento_id:
            return jsonify({'success': False, 'error': 'Transação não pode ser revertida'}), 400
        
        # Buscar evento relacionado
        evento = Evento.query.get(transacao.evento_id)
        if evento:
            # Reverter valor pago
            evento.valor_pago -= transacao.valor
            if evento.valor_pago < 0:
                evento.valor_pago = 0
            
            # Voltar status para Agendado se estava Realizado
            if evento.status == 'Realizado':
                evento.status = 'Agendado'
            
            # Restaurar/atualizar transação pendente
            saldo_restante = evento.valor_negociado - evento.valor_pago
            if saldo_restante > 0:
                pendente = Transacao.query.filter_by(
                    evento_id=evento.id,
                    tipo='Entrada Pendente'
                ).first()
                if pendente:
                    pendente.valor = saldo_restante
                    pendente.descricao = f'Saldo restante - {evento.cliente}'
                else:
                    nova_pendente = Transacao(
                        evento_id=evento.id,
                        tipo='Entrada Pendente',
                        valor=saldo_restante,
                        descricao=f'Saldo restante - {evento.cliente}',
                        data_transacao=evento.data_evento,
                        categoria='Pagamento de Cliente'
                    )
                    db.session.add(nova_pendente)
        
        # Excluir a transação de entrada
        db.session.delete(transacao)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao reverter pagamento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/transacao/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_transacao(id):
    try:
        transacao = Transacao.query.get_or_404(id)
        
        # Verificar se a transação está vinculada a um evento
        if transacao.evento_id:
            evento = Evento.query.get(transacao.evento_id)
            if evento:
                return jsonify({
                    'success': False, 
                    'error': f'Esta transação está vinculada ao evento de {evento.cliente}. Exclua o evento para remover todas as transações relacionadas.'
                }), 400
        
        # Se não está vinculada a evento, pode excluir
        db.session.delete(transacao)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/transacao/<int:id>/editar', methods=['POST'])
@login_required
def editar_transacao(id):
    try:
        transacao = Transacao.query.get_or_404(id)
        data = request.get_json()
        
        # Atualizar campos
        transacao.tipo = data.get('tipo', transacao.tipo)
        transacao.valor = float(data.get('valor', transacao.valor))
        transacao.descricao = data.get('descricao', transacao.descricao)
        transacao.data_transacao = datetime.strptime(data.get('data_transacao'), '%Y-%m-%d').date()
        transacao.categoria = data.get('categoria', transacao.categoria)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/importar')
@login_required
def importar():
    return render_template('importar.html')

@app.route('/importar/eventos', methods=['POST'])
@login_required
def importar_eventos():
    if 'arquivo' not in request.files:
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('importar'))
    
    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('importar'))
    
    if arquivo:
        filename = secure_filename(arquivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        arquivo.save(filepath)
        
        try:
            # Ler arquivo baseado na extensão
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(filepath)
            elif filename.endswith('.csv') or filename.endswith('.txt'):
                df = pd.read_csv(filepath, sep=';')
            else:
                flash('Formato de arquivo não suportado. Use Excel (.xlsx, .xls) ou CSV/TXT (.csv, .txt)', 'error')
                return redirect(url_for('importar'))
            
            # Mapear colunas esperadas
            colunas_esperadas = ['cliente', 'tipo_servico', 'data_evento', 'valor_negociado', 'valor_pago', 'status', 'observacoes']
            
            eventos_importados = 0
            for _, row in df.iterrows():
                try:
                    # Converter data
                    if pd.notna(row.get('data_evento')):
                        data_evento = pd.to_datetime(row['data_evento']).date()
                    else:
                        continue
                    
                    evento = Evento(
                        cliente=str(row.get('cliente', '')),
                        tipo_servico=str(row.get('tipo_servico', 'Fotografia')),
                        data_evento=data_evento,
                        valor_negociado=float(row.get('valor_negociado', 0)),
                        valor_pago=float(row.get('valor_pago', 0)),
                        status=str(row.get('status', 'Agendado')),
                        observacoes=str(row.get('observacoes', ''))
                    )
                    db.session.add(evento)
                    db.session.flush()
                    
                    # Criar transação pendente se há valor a receber
                    saldo = float(row.get('valor_negociado', 0)) - float(row.get('valor_pago', 0))
                    if saldo > 0:
                        pendente = Transacao(
                            evento_id=evento.id,
                            tipo='Entrada Pendente',
                            valor=saldo,
                            descricao=f'Saldo restante - {evento.cliente}',
                            data_transacao=evento.data_evento,
                            categoria='Pagamento de Cliente'
                        )
                        db.session.add(pendente)
                    
                    eventos_importados += 1
                except Exception as e:
                    continue
            
            db.session.commit()
            os.remove(filepath)  # Remover arquivo após importação
            
            flash(f'{eventos_importados} eventos importados com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro ao processar arquivo: {str(e)}', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return redirect(url_for('importar'))

@app.route('/importar/transacoes', methods=['POST'])
@login_required
def importar_transacoes():
    if 'arquivo' not in request.files:
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('importar'))
    
    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('importar'))
    
    if arquivo:
        filename = secure_filename(arquivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        arquivo.save(filepath)
        
        try:
            # Ler arquivo baseado na extensão
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(filepath)
            elif filename.endswith('.csv') or filename.endswith('.txt'):
                df = pd.read_csv(filepath, sep=';')
            else:
                flash('Formato de arquivo não suportado. Use Excel (.xlsx, .xls) ou CSV/TXT (.csv, .txt)', 'error')
                return redirect(url_for('importar'))
            
            transacoes_importadas = 0
            for _, row in df.iterrows():
                try:
                    # Converter data
                    if pd.notna(row.get('data_transacao')):
                        data_transacao = pd.to_datetime(row['data_transacao']).date()
                    else:
                        continue
                    
                    transacao = Transacao(
                        tipo=str(row.get('tipo', 'Entrada')),
                        valor=float(row.get('valor', 0)),
                        descricao=str(row.get('descricao', '')),
                        data_transacao=data_transacao,
                        categoria=str(row.get('categoria', ''))
                    )
                    db.session.add(transacao)
                    transacoes_importadas += 1
                except Exception as e:
                    continue
            
            db.session.commit()
            os.remove(filepath)  # Remover arquivo após importação
            
            flash(f'{transacoes_importadas} transações importadas com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro ao processar arquivo: {str(e)}', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return redirect(url_for('importar'))

@app.route('/api/dashboard-data')
@login_required
def dashboard_data():
    try:
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        periodo = request.args.get('periodo', 'ano')  # semana, mes, trimestre, ano, tudo
        hoje = date.today()
        
        if periodo == 'semana':
            data_inicio = hoje - timedelta(days=hoje.weekday())
            data_fim = data_inicio + timedelta(days=6)
        elif periodo == 'mes':
            data_inicio = hoje.replace(day=1)
            proximo_mes = data_inicio + relativedelta(months=1)
            data_fim = proximo_mes - timedelta(days=1)
        elif periodo == 'trimestre':
            trimestre_inicio = ((hoje.month - 1) // 3) * 3 + 1
            data_inicio = hoje.replace(month=trimestre_inicio, day=1)
            data_fim = data_inicio + relativedelta(months=3) - timedelta(days=1)
        elif periodo == 'ano':
            data_inicio = hoje.replace(month=1, day=1)
            data_fim = hoje.replace(month=12, day=31)
        else:  # tudo
            data_inicio = None
            data_fim = None
        
        def filtro_periodo(query):
            if data_inicio and data_fim:
                return query.filter(Evento.data_evento >= data_inicio, Evento.data_evento <= data_fim)
            return query
        
        # Receita PLANEJADA por mês
        q_plan = db.session.query(
            db.func.strftime('%Y-%m', Evento.data_evento).label('mes'),
            db.func.sum(Evento.valor_negociado).label('receita')
        )
        planejado_por_mes = filtro_periodo(q_plan).group_by('mes').order_by('mes').all()
        
        # Receita REAL por mês (excluindo cancelados)
        q_real = db.session.query(
            db.func.strftime('%Y-%m', Evento.data_evento).label('mes'),
            db.func.sum(Evento.valor_negociado).label('receita')
        ).filter(Evento.status != 'Cancelado')
        real_por_mes = filtro_periodo(q_real).group_by('mes').order_by('mes').all()
        
        # Recebido por mês
        q_rec = db.session.query(
            db.func.strftime('%Y-%m', Evento.data_evento).label('mes'),
            db.func.sum(Evento.valor_pago).label('receita')
        ).filter(Evento.valor_pago > 0)
        recebido_por_mes = filtro_periodo(q_rec).group_by('mes').order_by('mes').all()
        
        planejado_dict = {r.mes: float(r.receita or 0) for r in planejado_por_mes}
        real_dict = {r.mes: float(r.receita or 0) for r in real_por_mes}
        recebido_dict = {r.mes: float(r.receita or 0) for r in recebido_por_mes}
        
        todos_meses = sorted(set(list(planejado_dict.keys()) + list(real_dict.keys()) + list(recebido_dict.keys())))
        
        receita_completa = []
        for mes in todos_meses:
            receita_completa.append({
                'mes': mes,
                'planejado': planejado_dict.get(mes, 0),
                'real': real_dict.get(mes, 0),
                'recebido': recebido_dict.get(mes, 0)
            })
        
        # Serviços por tipo
        q_serv = db.session.query(
            Evento.tipo_servico,
            db.func.count(Evento.id).label('total')
        ).filter(Evento.status.in_(['Agendado', 'Realizado', 'Pendente']))
        servicos_por_tipo = filtro_periodo(q_serv).group_by(Evento.tipo_servico).all()
        
        # Totais do período para os cards
        q_totais = Evento.query
        if data_inicio and data_fim:
            q_totais = q_totais.filter(Evento.data_evento >= data_inicio, Evento.data_evento <= data_fim)
        eventos_periodo = q_totais.all()
        
        total_eventos = len(eventos_periodo)
        total_negociado = sum(e.valor_negociado for e in eventos_periodo if e.status != 'Cancelado')
        total_recebido = sum(e.valor_pago for e in eventos_periodo if e.status != 'Cancelado')
        agendados = sum(1 for e in eventos_periodo if e.status == 'Agendado')
        realizados = sum(1 for e in eventos_periodo if e.status == 'Realizado')
        cancelados = sum(1 for e in eventos_periodo if e.status == 'Cancelado')
        
        return jsonify({
            'receita_por_mes': receita_completa,
            'servicos_por_tipo': [{'tipo': s.tipo_servico, 'total': s.total} for s in servicos_por_tipo],
            'totais': {
                'total_eventos': total_eventos,
                'total_negociado': total_negociado,
                'total_recebido': total_recebido,
                'agendados': agendados,
                'realizados': realizados,
                'cancelados': cancelados
            }
        })
    except Exception as e:
        print(f"Erro na API dashboard-data: {e}")
        return jsonify({
            'receita_por_mes': [],
            'servicos_por_tipo': [],
            'totais': {}
        })

@app.route('/api/eventos-por-tipo')
@login_required
def eventos_por_tipo():
    tipo = request.args.get('tipo', '')
    try:
        query = Evento.query
        if tipo:
            query = query.filter(Evento.tipo_servico == tipo)
        eventos = query.order_by(Evento.data_evento.asc()).all()
        
        resultado = []
        for e in eventos:
            try:
                data_str = e.data_evento.strftime('%d/%m/%Y') if e.data_evento else '-'
            except:
                data_str = str(e.data_evento or '-')
            resultado.append({
                'id': e.id,
                'cliente': e.cliente or '',
                'data_evento': data_str,
                'status': e.status or '',
                'valor_negociado': float(e.valor_negociado or 0)
            })
        return jsonify(resultado)
    except Exception as ex:
        print(f"Erro em eventos-por-tipo: {ex}")
        return jsonify([])

@app.route('/api/eventos-calendario')
@login_required
def eventos_calendario():
    try:
        eventos = Evento.query.all()
        eventos_json = []
        
        for evento in eventos:
            try:
                data_evento = evento.data_evento.strftime('%Y-%m-%d') if evento.data_evento else ''
                data_cadastro = evento.data_cadastro.isoformat() if evento.data_cadastro else ''
            except (AttributeError, ValueError):
                data_evento = str(evento.data_evento or '')
                data_cadastro = str(evento.data_cadastro or '')
            
            eventos_json.append({
                'id': evento.id,
                'cliente': evento.cliente or '',
                'tipo_servico': evento.tipo_servico or '',
                'data_evento': data_evento,
                'valor_negociado': float(evento.valor_negociado or 0),
                'valor_pago': float(evento.valor_pago or 0),
                'status': evento.status or '',
                'observacoes': evento.observacoes or '',
                'data_cadastro': data_cadastro
            })
        
        return jsonify(eventos_json)
    except Exception as e:
        print(f"Erro na API eventos-calendario: {e}")
        return jsonify([])

@app.route('/api/alertas-eventos')
@login_required
def alertas_eventos():
    try:
        from datetime import timedelta
        hoje = date.today()
        uma_semana = hoje + timedelta(days=7)
        tres_dias = hoje + timedelta(days=3)
        
        # Eventos em 7 dias
        eventos_7_dias = Evento.query.filter(
            Evento.data_evento == uma_semana,
            Evento.status == 'Agendado'
        ).all()
        
        # Eventos em 3 dias
        eventos_3_dias = Evento.query.filter(
            Evento.data_evento == tres_dias,
            Evento.status == 'Agendado'
        ).all()
        
        alertas = []
        
        for evento in eventos_7_dias:
            alertas.append({
                'tipo': 'semana',
                'cliente': evento.cliente,
                'data': evento.data_evento.strftime('%d/%m/%Y'),
                'tipo_servico': evento.tipo_servico,
                'dias': 7
            })
        
        for evento in eventos_3_dias:
            alertas.append({
                'tipo': 'urgente',
                'cliente': evento.cliente,
                'data': evento.data_evento.strftime('%d/%m/%Y'),
                'tipo_servico': evento.tipo_servico,
                'dias': 3
            })
        
        return jsonify(alertas)
    except Exception as e:
        print(f"Erro na API alertas-eventos: {e}")
        return jsonify([])

# ---------------------------------------------------------------------------
# Rotas de Exportação
# ---------------------------------------------------------------------------

LOGO_PATH = os.path.join('static', 'img', 'photoflow_icon.png')


def _filtrar_eventos():
    """Aplica filtros de query string e retorna lista de eventos."""
    query = Evento.query
    cliente = request.args.get('cliente', '').strip()
    servico = request.args.get('servico', '').strip()
    data_de = request.args.get('data_de', '').strip()
    data_ate = request.args.get('data_ate', '').strip()
    status = request.args.get('status', '').strip()
    if cliente:
        query = query.filter(Evento.cliente.ilike(f'%{cliente}%'))
    if servico:
        query = query.filter(Evento.tipo_servico == servico)
    if data_de:
        query = query.filter(Evento.data_evento >= datetime.strptime(data_de, '%Y-%m-%d').date())
    if data_ate:
        query = query.filter(Evento.data_evento <= datetime.strptime(data_ate, '%Y-%m-%d').date())
    if status:
        query = query.filter(Evento.status == status)
    return query.order_by(Evento.data_evento.asc()).all()


def _eventos_to_dict(eventos):
    return [{
        'cliente': e.cliente, 'tipo_servico': e.tipo_servico,
        'data_evento': e.data_evento, 'ensaios_extras': e.ensaios_extras,
        'valor_negociado': e.valor_negociado, 'valor_pago': e.valor_pago,
        'status': e.status,
    } for e in eventos]


def _dados_caixa():
    """Retorna dados do caixa para exportação."""
    transacoes_realizadas = Transacao.query.filter(
        Transacao.tipo.in_(['Entrada', 'Saída'])
    ).order_by(Transacao.data_transacao.desc()).all()
    transacoes_pendentes = db.session.query(Transacao).join(
        Evento, Transacao.evento_id == Evento.id
    ).filter(
        Transacao.tipo == 'Entrada Pendente',
        Evento.status.notin_(['Cancelado']),
        Evento.valor_pago < Evento.valor_negociado
    ).order_by(Transacao.data_transacao.asc()).all()
    entradas = db.session.query(db.func.sum(Transacao.valor)).filter(Transacao.tipo == 'Entrada').scalar() or 0
    saidas = db.session.query(db.func.sum(Transacao.valor)).filter(Transacao.tipo == 'Saída').scalar() or 0
    saldo = entradas - saidas
    total_pendente = sum(t.valor for t in transacoes_pendentes)
    tx_dict = [{'data_transacao': t.data_transacao, 'tipo': t.tipo,
                'descricao': t.descricao, 'categoria': t.categoria or '',
                'valor': t.valor} for t in transacoes_realizadas]
    pend_dict = [{'data_transacao': t.data_transacao, 'descricao': t.descricao,
                  'valor': t.valor} for t in transacoes_pendentes]
    return tx_dict, pend_dict, entradas, saidas, saldo, total_pendente


@app.route('/exportar/eventos/excel')
@login_required
def exportar_eventos_excel():
    try:
        eventos = _filtrar_eventos()
        hoje = date.today()
        buf = export_utils.gerar_excel_eventos(_eventos_to_dict(eventos), hoje)
        return send_file(buf, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=f'eventos_{hoje.strftime("%Y-%m-%d")}.xlsx')
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar Excel: {str(e)}'}), 500


@app.route('/exportar/eventos/pdf')
@login_required
def exportar_eventos_pdf():
    try:
        eventos = _filtrar_eventos()
        hoje = date.today()
        buf = export_utils.gerar_pdf_eventos(_eventos_to_dict(eventos), hoje, LOGO_PATH)
        return send_file(buf, mimetype='application/pdf',
                         as_attachment=True, download_name=f'eventos_{hoje.strftime("%Y-%m-%d")}.pdf')
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500


@app.route('/exportar/caixa/excel')
@login_required
def exportar_caixa_excel():
    try:
        tx, pend, entradas, saidas, saldo, total_pend = _dados_caixa()
        hoje = date.today()
        buf = export_utils.gerar_excel_caixa(tx, pend, entradas, saidas, saldo, total_pend, hoje)
        return send_file(buf, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=f'caixa_{hoje.strftime("%Y-%m-%d")}.xlsx')
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar Excel: {str(e)}'}), 500


@app.route('/exportar/caixa/pdf')
@login_required
def exportar_caixa_pdf():
    try:
        tx, pend, entradas, saidas, saldo, _ = _dados_caixa()
        hoje = date.today()
        buf = export_utils.gerar_pdf_caixa(tx, pend, entradas, saidas, saldo, hoje, LOGO_PATH)
        return send_file(buf, mimetype='application/pdf',
                         as_attachment=True, download_name=f'caixa_{hoje.strftime("%Y-%m-%d")}.pdf')
        return send_file(buf, mimetype='application/pdf',
                         as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500


@app.route('/exportar/relatorio-mensal')
@login_required
def exportar_relatorio_mensal():
    try:
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        if not mes or not ano or mes < 1 or mes > 12 or ano < 2000:
            return jsonify({'error': 'Mês/ano inválido'}), 400

        # Eventos do mês (excluindo cancelados para totais)
        mes_str = f'{ano:04d}-{mes:02d}'
        eventos_mes = Evento.query.filter(
            db.func.strftime('%Y-%m', Evento.data_evento) == mes_str
        ).order_by(Evento.data_evento.asc()).all()

        eventos_dict = [{
            'cliente': e.cliente,
            'tipo_servico': e.tipo_servico,
            'data_evento': e.data_evento,
            'valor_negociado': e.valor_negociado,
            'valor_pago': e.valor_pago,
            'status': e.status,
        } for e in eventos_mes]

        # Transações do mês (Entrada e Saída)
        transacoes_mes = Transacao.query.filter(
            db.func.strftime('%Y-%m', Transacao.data_transacao) == mes_str,
            Transacao.tipo.in_(['Entrada', 'Saída'])
        ).order_by(Transacao.data_transacao.asc()).all()

        tx_dict = [{'data_transacao': t.data_transacao, 'tipo': t.tipo,
                     'descricao': t.descricao, 'categoria': t.categoria or '',
                     'valor': t.valor} for t in transacoes_mes]

        # Calcular resumo
        total_entradas = sum(t.valor for t in transacoes_mes if t.tipo == 'Entrada')
        total_saidas = sum(t.valor for t in transacoes_mes if t.tipo == 'Saída')
        eventos_nao_cancelados = [e for e in eventos_mes if e.status != 'Cancelado']
        total_negociado = sum(e.valor_negociado for e in eventos_nao_cancelados)
        total_recebido = sum(e.valor_pago for e in eventos_nao_cancelados)

        resumo = {
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_mes': total_entradas - total_saidas,
            'total_negociado': total_negociado,
            'total_recebido': total_recebido,
            'total_pendente': total_negociado - total_recebido,
        }

        buf = export_utils.gerar_pdf_relatorio_mensal(mes, ano, eventos_dict, tx_dict, resumo, LOGO_PATH)
        filename = f'relatorio_mensal_{ano:04d}-{mes:02d}.pdf'
        return send_file(buf, mimetype='application/pdf',
                         as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório: {str(e)}'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criar admin padrão se não existir nenhum usuário
        if not Usuario.query.first():
            admin = Usuario(username='admin', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)