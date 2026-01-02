#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a API e verificar dados
Execute: python testar_api.py
"""

from app import app, db, Evento, Transacao
from datetime import datetime, date

def verificar_dados():
    """Verifica os dados no banco"""
    with app.app_context():
        print("=== VERIFICANDO DADOS ===")
        
        # Contar eventos
        total_eventos = Evento.query.count()
        print(f"Total de eventos: {total_eventos}")
        
        if total_eventos > 0:
            print("\n=== PRIMEIROS 5 EVENTOS ===")
            eventos = Evento.query.limit(5).all()
            for evento in eventos:
                print(f"ID: {evento.id}")
                print(f"Cliente: {evento.cliente}")
                print(f"Tipo: {evento.tipo_servico}")
                print(f"Data: {evento.data_evento}")
                print(f"Valor Negociado: R$ {evento.valor_negociado}")
                print(f"Valor Pago: R$ {evento.valor_pago}")
                print(f"Status: {evento.status}")
                print("---")
        
        # Testar queries dos gráficos
        print("\n=== TESTANDO QUERIES DOS GRÁFICOS ===")
        
        # Receita por mês
        receita_query = db.session.query(
            db.func.strftime('%Y-%m', Evento.data_evento).label('mes'),
            db.func.sum(Evento.valor_pago).label('receita')
        ).filter(Evento.valor_pago > 0).group_by('mes').order_by('mes').all()
        
        print(f"Receita por mês - {len(receita_query)} registros:")
        for r in receita_query:
            print(f"  {r.mes}: R$ {r.receita}")
        
        # Serviços por tipo
        servicos_query = db.session.query(
            Evento.tipo_servico,
            db.func.count(Evento.id).label('total')
        ).group_by(Evento.tipo_servico).all()
        
        print(f"\nServiços por tipo - {len(servicos_query)} registros:")
        for s in servicos_query:
            print(f"  {s.tipo_servico}: {s.total} eventos")

def testar_api():
    """Testa a API diretamente"""
    with app.app_context():
        print("\n=== TESTANDO API ===")
        
        with app.test_client() as client:
            response = client.get('/api/dashboard-data')
            print(f"Status: {response.status_code}")
            print(f"Dados: {response.get_json()}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO COMPLETO")
    print("=" * 50)
    verificar_dados()
    testar_api()
    
    input("\nPressione Enter para continuar...")