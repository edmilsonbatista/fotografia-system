#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para acesso direto ao banco de dados
Execute: python acesso_banco.py
"""

from app import app, db, Evento, Transacao
from datetime import datetime, date

def listar_eventos():
    """Lista todos os eventos"""
    with app.app_context():
        eventos = Evento.query.all()
        print("\n=== EVENTOS ===")
        for evento in eventos:
            print(f"ID: {evento.id} | Cliente: {evento.cliente} | Data: {evento.data_evento} | Valor: R$ {evento.valor_negociado}")

def listar_transacoes():
    """Lista todas as transações"""
    with app.app_context():
        transacoes = Transacao.query.all()
        print("\n=== TRANSAÇÕES ===")
        for transacao in transacoes:
            print(f"ID: {transacao.id} | Tipo: {transacao.tipo} | Valor: R$ {transacao.valor} | Descrição: {transacao.descricao}")

def inserir_evento_exemplo():
    """Insere um evento de exemplo"""
    with app.app_context():
        evento = Evento(
            cliente="Cliente Teste",
            tipo_servico="Fotografia",
            data_evento=date(2024, 3, 15),
            valor_negociado=1000.00,
            valor_pago=400.00,
            status="Agendado",
            observacoes="Evento inserido via script"
        )
        db.session.add(evento)
        db.session.commit()
        print("✅ Evento inserido com sucesso!")

def inserir_transacao_exemplo():
    """Insere uma transação de exemplo"""
    with app.app_context():
        transacao = Transacao(
            tipo="Entrada",
            valor=400.00,
            descricao="Pagamento via script",
            data_transacao=date.today(),
            categoria="Pagamento de Cliente"
        )
        db.session.add(transacao)
        db.session.commit()
        print("✅ Transação inserida com sucesso!")

def executar_sql_customizado():
    """Executa SQL customizado"""
    with app.app_context():
        # Exemplo: Contar eventos por status
        resultado = db.session.execute("""
            SELECT status, COUNT(*) as total 
            FROM evento 
            GROUP BY status
        """).fetchall()
        
        print("\n=== EVENTOS POR STATUS ===")
        for row in resultado:
            print(f"{row[0]}: {row[1]} eventos")

if __name__ == "__main__":
    print("🗄️  ACESSO DIRETO AO BANCO DE DADOS")
    print("1. Listar eventos")
    print("2. Listar transações")
    print("3. Inserir evento exemplo")
    print("4. Inserir transação exemplo")
    print("5. Executar SQL customizado")
    print("0. Sair")
    
    while True:
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            listar_eventos()
        elif opcao == "2":
            listar_transacoes()
        elif opcao == "3":
            inserir_evento_exemplo()
        elif opcao == "4":
            inserir_transacao_exemplo()
        elif opcao == "5":
            executar_sql_customizado()
        elif opcao == "0":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida!")