from app import app, db, Transacao

with app.app_context():
    # Excluir todas as transações
    transacoes_excluidas = Transacao.query.count()
    Transacao.query.delete()
    db.session.commit()
    
    print(f"✅ {transacoes_excluidas} transações excluídas do caixa!")
    print("Dados de caixa limpos com sucesso.")