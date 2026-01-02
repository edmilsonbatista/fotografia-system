from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fotografia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Filtro personalizado para formatação brasileira
@app.template_filter('moeda')
def moeda_filter(valor):
    """Formata valor como moeda brasileira"""
    if valor is None:
        valor = 0
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

@app.template_filter('numero')
def numero_filter(valor):
    """Formata número com separador de milhares brasileiro"""
    if valor is None:
        valor = 0
    return f"{valor:,.0f}".replace(',', '.')

# Criar pasta de uploads se não existir
if not os.path.exists('uploads'):
    os.makedirs('uploads')

db = SQLAlchemy(app)

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

class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'))
    tipo = db.Column(db.String(20), nullable=False)  # Entrada, Saída
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    data_transacao = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(50))  # Equipamento, Transporte, etc.

# Rotas
@app.route('/')
def dashboard():
    hoje = date.today()
    
    # Estatísticas básicas
    total_eventos = Evento.query.count()
    eventos_mes = Evento.query.filter(
        db.func.strftime('%Y-%m', Evento.data_evento) == hoje.strftime('%Y-%m')
    ).count()
    
    # Receitas (baseadas em valor_pago - dinheiro realmente recebido)
    receita_total = db.session.query(db.func.sum(Evento.valor_pago)).scalar() or 0
    receita_mes = db.session.query(db.func.sum(Evento.valor_pago)).filter(
        db.func.strftime('%Y-%m', Evento.data_evento) == hoje.strftime('%Y-%m')
    ).scalar() or 0
    
    # Status dos eventos
    eventos_agendados = Evento.query.filter_by(status='Agendado').count()
    eventos_realizados = Evento.query.filter_by(status='Realizado').count()
    eventos_cancelados = Evento.query.filter_by(status='Cancelado').count()
    
    # Valores financeiros totais
    todos_eventos = Evento.query.all()
    total_negociado = sum(e.valor_negociado for e in todos_eventos)
    total_recebido = sum(e.valor_pago for e in todos_eventos)
    total_pendente = total_negociado - total_recebido
    
    # Próximos eventos (5 mais próximos por data)
    proximos_eventos = Evento.query.order_by(Evento.data_evento.asc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_eventos=total_eventos,
                         eventos_mes=eventos_mes,
                         receita_total=receita_total,
                         receita_mes=receita_mes,
                         eventos_agendados=eventos_agendados,
                         eventos_realizados=eventos_realizados,
                         eventos_cancelados=eventos_cancelados,
                         total_negociado=total_negociado,
                         total_recebido=total_recebido,
                         total_pendente=total_pendente,
                         proximos_eventos=proximos_eventos,
                         eventos=todos_eventos)

@app.route('/eventos')
def listar_eventos():
    eventos = Evento.query.order_by(Evento.data_evento.asc()).all()
    return render_template('eventos.html', eventos=eventos)

@app.route('/evento/novo', methods=['GET', 'POST'])
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
        db.session.commit()
        return redirect(url_for('listar_eventos'))
    
    return render_template('novo_evento.html')

@app.route('/evento/<int:id>/pagar', methods=['POST'])
def registrar_pagamento(id):
    try:
        data = request.get_json()
        valor = float(data['valor'])
        
        evento = Evento.query.get_or_404(id)
        evento.valor_pago += valor
        
        # Criar transação no caixa
        transacao = Transacao(
            evento_id=id,
            tipo='Entrada',
            valor=valor,
            descricao=f'Pagamento - {evento.cliente}',
            data_transacao=date.today(),
            categoria='Pagamento de Cliente'
        )
        db.session.add(transacao)
        
        if evento.valor_pago >= evento.valor_negociado:
            evento.status = 'Realizado'
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Erro no pagamento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/caixa')
def caixa():
    transacoes = Transacao.query.order_by(Transacao.data_transacao.desc()).all()
    
    # Separar transações realizadas e pendentes
    transacoes_realizadas = [t for t in transacoes if t.tipo in ['Entrada', 'Saída']]
    transacoes_pendentes = [t for t in transacoes if t.tipo == 'Entrada Pendente']
    
    # Calcular saldos
    entradas = db.session.query(db.func.sum(Transacao.valor)).filter(Transacao.tipo == 'Entrada').scalar() or 0
    saidas = db.session.query(db.func.sum(Transacao.valor)).filter(Transacao.tipo == 'Saída').scalar() or 0
    pendentes = db.session.query(db.func.sum(Transacao.valor)).filter(Transacao.tipo == 'Entrada Pendente').scalar() or 0
    
    saldo_atual = entradas - saidas
    saldo_projetado = saldo_atual + pendentes
    
    return render_template('caixa.html', 
                         transacoes=transacoes_realizadas,
                         transacoes_pendentes=transacoes_pendentes,
                         saldo=saldo_atual,
                         saldo_projetado=saldo_projetado,
                         total_pendente=pendentes)

@app.route('/transacao/nova', methods=['POST'])
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
def excluir_evento(id):
    evento = Evento.query.get_or_404(id)
    db.session.delete(evento)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/evento/<int:id>/editar', methods=['POST'])
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
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/transacao/<int:id>/reverter', methods=['POST'])
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
        
        # Excluir a transação
        db.session.delete(transacao)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao reverter pagamento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/transacao/<int:id>/excluir', methods=['POST'])
def excluir_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    db.session.delete(transacao)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/importar')
def importar():
    return render_template('importar.html')

@app.route('/importar/eventos', methods=['POST'])
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
def dashboard_data():
    try:
        # Receita por mês (baseada no valor negociado)
        receita_por_mes = db.session.query(
            db.func.strftime('%Y-%m', Evento.data_evento).label('mes'),
            db.func.sum(Evento.valor_negociado).label('receita')
        ).group_by('mes').order_by('mes').all()
        
        # Serviços por tipo (todos os eventos)
        servicos_por_tipo = db.session.query(
            Evento.tipo_servico,
            db.func.count(Evento.id).label('total')
        ).group_by(Evento.tipo_servico).all()
        
        return jsonify({
            'receita_por_mes': [{'mes': r.mes, 'receita': float(r.receita or 0)} for r in receita_por_mes],
            'servicos_por_tipo': [{'tipo': s.tipo_servico, 'total': s.total} for s in servicos_por_tipo]
        })
    except Exception as e:
        print(f"Erro na API dashboard-data: {e}")
        return jsonify({
            'receita_por_mes': [],
            'servicos_por_tipo': []
        })

@app.route('/api/eventos-calendario')
def eventos_calendario():
    try:
        eventos = Evento.query.all()
        eventos_json = []
        
        for evento in eventos:
            eventos_json.append({
                'id': evento.id,
                'cliente': evento.cliente,
                'tipo_servico': evento.tipo_servico,
                'data_evento': evento.data_evento.strftime('%Y-%m-%d'),
                'valor_negociado': float(evento.valor_negociado),
                'valor_pago': float(evento.valor_pago),
                'status': evento.status,
                'observacoes': evento.observacoes or '',
                'data_cadastro': evento.data_cadastro.isoformat()
            })
        
        return jsonify(eventos_json)
    except Exception as e:
        print(f"Erro na API eventos-calendario: {e}")
        return jsonify([])

@app.route('/api/alertas-eventos')
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)