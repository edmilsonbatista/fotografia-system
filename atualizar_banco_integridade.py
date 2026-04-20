"""
Script para atualizar o banco de dados e garantir integridade referencial
entre eventos e transações
"""
from app import app, db, Evento, Transacao

def verificar_integridade():
    """Verifica a integridade dos dados"""
    with app.app_context():
        print("="*60)
        print("VERIFICAÇÃO DE INTEGRIDADE - EVENTOS E TRANSAÇÕES")
        print("="*60)
        
        # 1. Verificar transações órfãs (sem evento válido)
        print("\n1. Verificando transações órfãs...")
        transacoes_orfas = []
        
        transacoes_com_evento = Transacao.query.filter(Transacao.evento_id.isnot(None)).all()
        
        for transacao in transacoes_com_evento:
            evento = Evento.query.get(transacao.evento_id)
            if not evento:
                transacoes_orfas.append(transacao)
        
        if transacoes_orfas:
            print(f"   ⚠️  Encontradas {len(transacoes_orfas)} transações órfãs:")
            for t in transacoes_orfas:
                print(f"      ID {t.id}: {t.descricao} (Evento ID {t.evento_id} não existe)")
        else:
            print("   ✅ Nenhuma transação órfã encontrada")
        
        # 2. Verificar eventos sem transação pendente
        print("\n2. Verificando eventos sem transação pendente...")
        eventos_sem_transacao = []
        
        eventos = Evento.query.filter(Evento.status != 'Cancelado').all()
        
        for evento in eventos:
            saldo_pendente = evento.valor_negociado - evento.valor_pago
            if saldo_pendente > 0:
                transacao_pendente = Transacao.query.filter_by(
                    evento_id=evento.id,
                    tipo='Entrada Pendente'
                ).first()
                
                if not transacao_pendente:
                    eventos_sem_transacao.append({
                        'evento': evento,
                        'saldo': saldo_pendente
                    })
        
        if eventos_sem_transacao:
            print(f"   ⚠️  Encontrados {len(eventos_sem_transacao)} eventos sem transação pendente:")
            for item in eventos_sem_transacao:
                e = item['evento']
                print(f"      ID {e.id}: {e.cliente} - Saldo: R$ {item['saldo']:.2f}")
        else:
            print("   ✅ Todos os eventos com saldo têm transação pendente")
        
        # 3. Verificar inconsistências de valores
        print("\n3. Verificando inconsistências de valores...")
        inconsistencias = []
        
        for evento in eventos:
            transacoes_entrada = Transacao.query.filter_by(
                evento_id=evento.id,
                tipo='Entrada'
            ).all()
            
            total_transacoes = sum(t.valor for t in transacoes_entrada)
            
            if abs(total_transacoes - evento.valor_pago) > 0.01:  # Tolerância de 1 centavo
                inconsistencias.append({
                    'evento': evento,
                    'valor_evento': evento.valor_pago,
                    'valor_transacoes': total_transacoes,
                    'diferenca': evento.valor_pago - total_transacoes
                })
        
        if inconsistencias:
            print(f"   ⚠️  Encontradas {len(inconsistencias)} inconsistências:")
            for item in inconsistencias:
                e = item['evento']
                print(f"      ID {e.id}: {e.cliente}")
                print(f"         Valor pago no evento: R$ {item['valor_evento']:.2f}")
                print(f"         Valor nas transações: R$ {item['valor_transacoes']:.2f}")
                print(f"         Diferença: R$ {item['diferenca']:.2f}")
        else:
            print("   ✅ Valores consistentes entre eventos e transações")
        
        print("\n" + "="*60)
        print("RESUMO:")
        print(f"  • Transações órfãs: {len(transacoes_orfas)}")
        print(f"  • Eventos sem transação pendente: {len(eventos_sem_transacao)}")
        print(f"  • Inconsistências de valores: {len(inconsistencias)}")
        print("="*60)
        
        return {
            'transacoes_orfas': transacoes_orfas,
            'eventos_sem_transacao': eventos_sem_transacao,
            'inconsistencias': inconsistencias
        }

def corrigir_problemas():
    """Corrige os problemas encontrados"""
    with app.app_context():
        resultado = verificar_integridade()
        
        if not any([
            resultado['transacoes_orfas'],
            resultado['eventos_sem_transacao'],
            resultado['inconsistencias']
        ]):
            print("\n✅ Nenhum problema encontrado! Banco de dados íntegro.")
            return
        
        print("\n" + "="*60)
        print("CORREÇÃO DE PROBLEMAS")
        print("="*60)
        
        resposta = input("\nDeseja corrigir os problemas encontrados? (S/N): ").strip().upper()
        
        if resposta != 'S':
            print("\n❌ Operação cancelada.")
            return
        
        # Corrigir transações órfãs
        if resultado['transacoes_orfas']:
            print("\n🔧 Removendo transações órfãs...")
            for transacao in resultado['transacoes_orfas']:
                print(f"   ✓ Removendo transação ID {transacao.id}")
                db.session.delete(transacao)
        
        # Criar transações pendentes faltantes
        if resultado['eventos_sem_transacao']:
            print("\n🔧 Criando transações pendentes...")
            for item in resultado['eventos_sem_transacao']:
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
                print(f"   ✓ Transação criada para evento ID {evento.id}")
        
        db.session.commit()
        
        print("\n✅ Correções aplicadas com sucesso!")
        print("\n🔄 Executando nova verificação...")
        verificar_integridade()

def testar_exclusao_cascata():
    """Testa se a exclusão em cascata está funcionando"""
    with app.app_context():
        print("\n" + "="*60)
        print("TESTE DE EXCLUSÃO EM CASCATA")
        print("="*60)
        
        # Criar evento de teste
        print("\n1. Criando evento de teste...")
        evento_teste = Evento(
            cliente='TESTE - Não Excluir Manualmente',
            tipo_servico='Fotografia',
            data_evento=db.func.current_date(),
            valor_negociado=100.00,
            status='Agendado'
        )
        db.session.add(evento_teste)
        db.session.flush()
        
        # Criar transação vinculada
        print("2. Criando transação vinculada...")
        transacao_teste = Transacao(
            evento_id=evento_teste.id,
            tipo='Entrada Pendente',
            valor=100.00,
            descricao='Teste de integridade',
            data_transacao=db.func.current_date(),
            categoria='Teste'
        )
        db.session.add(transacao_teste)
        db.session.commit()
        
        evento_id = evento_teste.id
        transacao_id = transacao_teste.id
        
        print(f"   ✓ Evento criado: ID {evento_id}")
        print(f"   ✓ Transação criada: ID {transacao_id}")
        
        # Excluir evento
        print("\n3. Excluindo evento...")
        db.session.delete(evento_teste)
        db.session.commit()
        
        # Verificar se transação foi excluída
        print("4. Verificando se transação foi excluída automaticamente...")
        transacao_existe = Transacao.query.get(transacao_id)
        
        if transacao_existe:
            print("   ❌ FALHA: Transação ainda existe!")
            print("   ⚠️  A exclusão em cascata NÃO está funcionando!")
            # Limpar
            db.session.delete(transacao_existe)
            db.session.commit()
        else:
            print("   ✅ SUCESSO: Transação foi excluída automaticamente!")
            print("   ✅ Exclusão em cascata está funcionando corretamente!")
        
        print("="*60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'verificar':
            verificar_integridade()
        elif sys.argv[1] == 'corrigir':
            corrigir_problemas()
        elif sys.argv[1] == 'testar':
            testar_exclusao_cascata()
        else:
            print("Uso: python atualizar_banco_integridade.py [verificar|corrigir|testar]")
    else:
        # Menu interativo
        while True:
            print("\n" + "="*60)
            print("INTEGRIDADE DO BANCO DE DADOS")
            print("="*60)
            print("1. Verificar integridade")
            print("2. Corrigir problemas")
            print("3. Testar exclusão em cascata")
            print("0. Sair")
            print("="*60)
            
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == '1':
                verificar_integridade()
            elif opcao == '2':
                corrigir_problemas()
            elif opcao == '3':
                testar_exclusao_cascata()
            elif opcao == '0':
                print("\n👋 Encerrando...")
                break
            else:
                print("\n❌ Opção inválida!")
