from app import app, db, Evento, Transacao
from datetime import datetime, date, timedelta
import random

def criar_dados_exemplo():
    """Cria dados de exemplo para demonstrar o sistema"""
    
    with app.app_context():
        # Limpar dados existentes
        db.drop_all()
        db.create_all()
        
        # Eventos de exemplo
        eventos_exemplo = [
            {
                'cliente': 'Maria Silva',
                'tipo_servico': 'Fotografia',
                'data_evento': date.today() + timedelta(days=7),
                'valor_negociado': 800.00,
                'valor_pago': 400.00,
                'status': 'Agendado',
                'observacoes': 'Casamento na igreja São José, 200 convidados'
            },
            {
                'cliente': 'João Santos',
                'tipo_servico': 'Storymaker',
                'data_evento': date.today() + timedelta(days=15),
                'valor_negociado': 1200.00,
                'valor_pago': 0.00,
                'status': 'Agendado',
                'observacoes': 'Vídeo institucional para empresa, 3 minutos'
            },
            {
                'cliente': 'Ana Costa',
                'tipo_servico': 'Fotografia + Storymaker',
                'data_evento': date.today() - timedelta(days=5),
                'valor_negociado': 1800.00,
                'valor_pago': 1800.00,
                'status': 'Realizado',
                'observacoes': 'Aniversário de 15 anos, salão de festas'
            },
            {
                'cliente': 'Carlos Oliveira',
                'tipo_servico': 'Fotografia',
                'data_evento': date.today() - timedelta(days=12),
                'valor_negociado': 600.00,
                'valor_pago': 600.00,
                'status': 'Realizado',
                'observacoes': 'Ensaio fotográfico em estúdio'
            },
            {
                'cliente': 'Fernanda Lima',
                'tipo_servico': 'Storymaker',
                'data_evento': date.today() + timedelta(days=30),
                'valor_negociado': 900.00,
                'valor_pago': 300.00,
                'status': 'Agendado',
                'observacoes': 'Documentário sobre a família, 2 dias de gravação'
            }
        ]
        
        for evento_data in eventos_exemplo:
            evento = Evento(**evento_data)
            db.session.add(evento)
        
        # Transações de exemplo
        transacoes_exemplo = [
            {
                'tipo': 'Entrada',
                'valor': 400.00,
                'descricao': 'Sinal do casamento - Maria Silva',
                'data_transacao': date.today() - timedelta(days=3),
                'categoria': 'Pagamento de Cliente'
            },
            {
                'tipo': 'Entrada',
                'valor': 1800.00,
                'descricao': 'Pagamento completo - Ana Costa',
                'data_transacao': date.today() - timedelta(days=5),
                'categoria': 'Pagamento de Cliente'
            },
            {
                'tipo': 'Entrada',
                'valor': 600.00,
                'descricao': 'Ensaio fotográfico - Carlos Oliveira',
                'data_transacao': date.today() - timedelta(days=12),
                'categoria': 'Pagamento de Cliente'
            },
            {
                'tipo': 'Entrada',
                'valor': 300.00,
                'descricao': 'Sinal documentário - Fernanda Lima',
                'data_transacao': date.today() - timedelta(days=2),
                'categoria': 'Pagamento de Cliente'
            },
            {
                'tipo': 'Saída',
                'valor': 150.00,
                'descricao': 'Combustível para evento',
                'data_transacao': date.today() - timedelta(days=5),
                'categoria': 'Transporte'
            },
            {
                'tipo': 'Saída',
                'valor': 80.00,
                'descricao': 'Almoço durante evento',
                'data_transacao': date.today() - timedelta(days=5),
                'categoria': 'Alimentação'
            },
            {
                'tipo': 'Saída',
                'valor': 200.00,
                'descricao': 'Manutenção da câmera',
                'data_transacao': date.today() - timedelta(days=10),
                'categoria': 'Manutenção'
            },
            {
                'tipo': 'Saída',
                'valor': 120.00,
                'descricao': 'Anúncio no Facebook',
                'data_transacao': date.today() - timedelta(days=7),
                'categoria': 'Marketing'
            }
        ]
        
        for transacao_data in transacoes_exemplo:
            transacao = Transacao(**transacao_data)
            db.session.add(transacao)
        
        # Salvar todas as alterações
        db.session.commit()
        
        print("Dados de exemplo criados com sucesso!")
        print("\nResumo dos dados criados:")
        print(f"   - {len(eventos_exemplo)} eventos")
        print(f"   - {len(transacoes_exemplo)} transacoes")
        print(f"   - Receita total: R$ {sum(t['valor'] for t in transacoes_exemplo if t['tipo'] == 'Entrada'):.2f}")
        print(f"   - Gastos totais: R$ {sum(t['valor'] for t in transacoes_exemplo if t['tipo'] == 'Saída'):.2f}")
        print("\nExecute 'python app.py' para iniciar o sistema!")

if __name__ == '__main__':
    criar_dados_exemplo()