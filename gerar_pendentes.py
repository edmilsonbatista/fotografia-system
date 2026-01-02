from app import app, db, Evento, Transacao
from datetime import date

def gerar_entradas_pendentes():
    """Gera transações de entrada pendentes para eventos já cadastrados"""
    
    with app.app_context():
        # Buscar eventos que têm valor a receber
        eventos_pendentes = Evento.query.filter(Evento.valor_pago < Evento.valor_negociado).all()
        
        transacoes_criadas = 0
        
        for evento in eventos_pendentes:
            valor_pendente = evento.valor_negociado - evento.valor_pago
            
            # Verificar se já existe transação pendente para este evento
            transacao_existente = Transacao.query.filter_by(
                evento_id=evento.id,
                tipo='Entrada Pendente'
            ).first()
            
            if not transacao_existente and valor_pendente > 0:
                # Criar transação pendente
                transacao = Transacao(
                    evento_id=evento.id,
                    tipo='Entrada Pendente',
                    valor=valor_pendente,
                    descricao=f'A receber - {evento.cliente}',
                    data_transacao=evento.data_evento,
                    categoria='Pagamento de Cliente'
                )
                db.session.add(transacao)
                transacoes_criadas += 1
        
        db.session.commit()
        
        print(f"✅ {transacoes_criadas} entradas pendentes criadas!")
        print(f"📊 {len(eventos_pendentes)} eventos com valores a receber")
        
        # Mostrar resumo
        total_pendente = sum(e.valor_negociado - e.valor_pago for e in eventos_pendentes)
        print(f"💰 Total a receber: R$ {total_pendente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

if __name__ == "__main__":
    gerar_entradas_pendentes()