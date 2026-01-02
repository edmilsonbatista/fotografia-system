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
    # Estatísticas para o dashboard
    total_eventos = Evento.query.count()
    eventos_mes = Evento.query.filter(
        Evento.data_evento >= date.today().replace(day=1)
    ).count()
    
    receita_total = db.session.query(db.func.sum(Evento.valor_pago)).scalar() or 0
    receita_mes = db.session.query(db.func.sum(Evento.valor_pago)).filter(
        Evento.data_evento >= date.today().replace(day=1)
    ).scalar() or 0
    
    # Eventos por status
    eventos_agendados = Evento.query.filter_by(status='Agendado').count()
    eventos_realizados = Evento.query.filter_by(status='Realizado').count()
    
    # Próximos eventos
    proximos_eventos = Evento.query.filter(
        Evento.data_evento >= date.today(),
        Evento.status == 'Agendado'
    ).order_by(Evento.data_evento).limit(5).all()
    
    return render_template('dashboard.html',
                         total_eventos=total_eventos,
                         eventos_mes=eventos_mes,
                         receita_total=receita_total,
                         receita_mes=receita_mes,
                         eventos_agendados=eventos_agendados,
                         eventos_realizados=eventos_realizados,
                         proximos_eventos=proximos_eventos)

@app.route('/eventos')
def listar_eventos():
    eventos = Evento.query.order_by(Evento.data_evento.desc()).all()
    return render_template('eventos.html', eventos=eventos)

@app.route('/evento/novo', methods=['GET', 'POST'])
def novo_evento():
    if request.method == 'POST':
        evento = Evento(
            cliente=request.form['cliente'],
            tipo_servico=request.form['tipo_servico'],
            data_evento=datetime.strptime(request.form['data_evento'], '%Y-%m-%d').date(),
            valor_negociado=float(request.form['valor_negociado']),
            observacoes=request.form.get('observacoes', '')
        )
        db.session.add(evento)
        db.session.commit()
        return redirect(url_for('listar_eventos'))
    
    return render_template('novo_evento.html')

@app.route('/evento/<int:id>/pagar', methods=['POST'])
def registrar_pagamento():
    evento_id = request.json['evento_id']
    valor = float(request.json['valor'])
    
    evento = Evento.query.get(evento_id)
    evento.valor_pago += valor
    
    if evento.valor_pago >= evento.valor_negociado:
        evento.status = 'Realizado'
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/caixa')
def caixa():
    transacoes = Transacao.query.order_by(Transacao.data_transacao.desc()).all()
    saldo = db.session.query(
        db.func.sum(db.case([(Transacao.tipo == 'Entrada', Transacao.valor)], else_=0)) -
        db.func.sum(db.case([(Transacao.tipo == 'Saída', Transacao.valor)], else_=0))
    ).scalar() or 0
    
    return render_template('caixa.html', transacoes=transacoes, saldo=saldo)

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
    
    evento.cliente = request.json.get('cliente', evento.cliente)
    evento.tipo_servico = request.json.get('tipo_servico', evento.tipo_servico)
    evento.data_evento = datetime.strptime(request.json.get('data_evento'), '%Y-%m-%d').date() if request.json.get('data_evento') else evento.data_evento
    evento.valor_negociado = float(request.json.get('valor_negociado', evento.valor_negociado))
    evento.valor_pago = float(request.json.get('valor_pago', evento.valor_pago))
    evento.status = request.json.get('status', evento.status)
    evento.observacoes = request.json.get('observacoes', evento.observacoes)
    
    db.session.commit()
    return jsonify({'success': True})

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
    # Dados para gráficos
    eventos_por_mes = db.session.query(
        db.func.strftime('%Y-%m', Evento.data_evento).label('mes'),
        db.func.count(Evento.id).label('total')
    ).group_by('mes').all()
    
    receita_por_mes = db.session.query(
        db.func.strftime('%Y-%m', Evento.data_evento).label('mes'),
        db.func.sum(Evento.valor_pago).label('receita')
    ).group_by('mes').all()
    
    servicos_por_tipo = db.session.query(
        Evento.tipo_servico,
        db.func.count(Evento.id).label('total')
    ).group_by(Evento.tipo_servico).all()
    
    return jsonify({
        'eventos_por_mes': [{'mes': e.mes, 'total': e.total} for e in eventos_por_mes],
        'receita_por_mes': [{'mes': r.mes, 'receita': r.receita or 0} for r in receita_por_mes],
        'servicos_por_tipo': [{'tipo': s.tipo_servico, 'total': s.total} for s in servicos_por_tipo]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)