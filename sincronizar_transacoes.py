from app import app, db, Evento, Transacao
from datetime import datetime

def sincronizar_transacoes_pendentes():
    """
    Verifica eventos sem transação pendente e cria automaticamente
    """
    with app.app_context():
        print("="*60)
        print("SINCRONIZAÇÃO DE TRANSAÇÕES PENDENTES")
        print("="*60)
        
        # Buscar todos os eventos que não estão cancelados
        eventos = Evento.query.filter(Evento.status != 'Cancelado').all()
        
        eventos_sem_transacao = []
        eventos_com_saldo_pendente = []
        
        for evento in eventos:
            # Verificar se existe transação pendente para este evento
            transacao_pendente = Transacao.query.filter_by(
                evento_id=evento.id,
                tipo='Entrada Pendente'
            ).first()
            
            saldo_pendente = evento.valor_negociado - evento.valor_pago
            
            # Se não tem transação pendente e ainda tem saldo a receber
            if not transacao_pendente and saldo_pendente > 0:
                eventos_sem_transacao.append({
                    'evento': evento,
                    'saldo': saldo_pendente
                })
        
        if not eventos_sem_transacao:
            print("\n✅ Todos os eventos estão sincronizados!")
            print(f"Total de eventos verificados: {len(eventos)}")
            return
        
        print(f"\n⚠️  Encontrados {len(eventos_sem_transacao)} eventos sem transação pendente:\n")
        
        for item in eventos_sem_transacao:
            evento = item['evento']
            saldo = item['saldo']
            print(f"ID {evento.id}: {evento.cliente}")
            print(f"   Data: {evento.data_evento.strftime('%d/%m/%Y')}")
            print(f"   Valor Negociado: R$ {evento.valor_negociado:.2f}")
            print(f"   Valor Pago: R$ {evento.valor_pago:.2f}")
            print(f"   Saldo Pendente: R$ {saldo:.2f}")
            print(f"   Status: {evento.status}")
            print()
        
        resposta = input("Deseja criar transações pendentes para esses eventos? (S/N): ").strip().upper()
        
        if resposta != 'S':
            print("\n❌ Operação cancelada.")
            return
        
        print("\n🔄 Criando transações pendentes...\n")
        
        criadas = 0
        for item in eventos_sem_transacao:
            evento = item['evento']
            saldo = item['saldo']
            
            transacao = Transacao(
                evento_id=evento.id,
                tipo='Entrada Pendente',
                valor=saldo,
                descricao=f'Saldo restante - {evento.cliente}',
                data_transacao=evento.data_evento,
                categoria='Pagamento de Cliente'
            )
            db.session.add(transacao)
            criadas += 1
            print(f"✓ Transação criada para: {evento.cliente} - R$ {saldo:.2f}")
        
        db.session.commit()
        
        print(f"\n✅ {criadas} transações pendentes criadas com sucesso!")
        print("="*60)

def listar_todas_transacoes():
    """
    Lista todas as transações pendentes cadastradas
    """
    with app.app_context():
        print("\n" + "="*60)
        print("TRANSAÇÕES PENDENTES CADASTRADAS")
        print("="*60)
        
        transacoes = Transacao.query.filter_by(tipo='Entrada Pendente').order_by(Transacao.data_transacao).all()
        
        if not transacoes:
            print("\n❌ Nenhuma transação pendente encontrada.")
            return
        
        total = 0
        for t in transacoes:
            evento = Evento.query.get(t.evento_id) if t.evento_id else None
            print(f"\nID: {t.id}")
            print(f"Evento ID: {t.evento_id}")
            if evento:
                print(f"Cliente: {evento.cliente}")
                print(f"Status Evento: {evento.status}")
            print(f"Descrição: {t.descricao}")
            print(f"Valor: R$ {t.valor:.2f}")
            print(f"Data: {t.data_transacao.strftime('%d/%m/%Y')}")
            total += t.valor
        
        print(f"\n{'='*60}")
        print(f"Total de transações pendentes: {len(transacoes)}")
        print(f"Valor total pendente: R$ {total:.2f}")
        print("="*60)

def menu():
    """Menu interativo"""
    while True:
        print("\n" + "="*60)
        print("SINCRONIZAÇÃO DE TRANSAÇÕES - MENU")
        print("="*60)
        print("1. Verificar e sincronizar eventos sem transação")
        print("2. Listar todas as transações pendentes")
        print("3. Verificar eventos com pagamento mas sem baixa na transação")
        print("0. Sair")
        print("="*60)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            sincronizar_transacoes_pendentes()
        elif opcao == '2':
            listar_todas_transacoes()
        elif opcao == '3':
            verificar_pagamentos_sem_baixa()
        elif opcao == '0':
            print("\n👋 Encerrando...")
            break
        else:
            print("\n❌ Opção inválida!")

def verificar_pagamentos_sem_baixa():
    """
    Verifica eventos que receberam pagamento mas a transação pendente não foi baixada
    """
    with app.app_context():
        print("\n" + "="*60)
        print("VERIFICAR PAGAMENTOS SEM BAIXA")
        print("="*60)
        
        eventos = Evento.query.filter(Evento.valor_pago > 0).all()
        
        problemas = []
        
        for evento in eventos:
            # Buscar transação pendente
            transacao_pendente = Transacao.query.filter_by(
                evento_id=evento.id,
                tipo='Entrada Pendente'
            ).first()
            
            # Buscar transações de entrada (pagamentos realizados)
            transacoes_entrada = Transacao.query.filter_by(
                evento_id=evento.id,
                tipo='Entrada'
            ).all()
            
            total_pago_transacoes = sum(t.valor for t in transacoes_entrada)
            
            # Se o valor pago no evento não bate com as transações
            if evento.valor_pago != total_pago_transacoes:
                problemas.append({
                    'evento': evento,
                    'valor_evento': evento.valor_pago,
                    'valor_transacoes': total_pago_transacoes,
                    'diferenca': evento.valor_pago - total_pago_transacoes
                })
        
        if not problemas:
            print("\n✅ Todos os pagamentos estão sincronizados!")
            return
        
        print(f"\n⚠️  Encontrados {len(problemas)} eventos com divergência:\n")
        
        for item in problemas:
            evento = item['evento']
            print(f"ID {evento.id}: {evento.cliente}")
            print(f"   Valor pago no evento: R$ {item['valor_evento']:.2f}")
            print(f"   Valor nas transações: R$ {item['valor_transacoes']:.2f}")
            print(f"   Diferença: R$ {item['diferenca']:.2f}")
            print()

if __name__ == '__main__':
    menu()
