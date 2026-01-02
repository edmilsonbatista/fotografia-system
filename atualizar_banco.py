#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar coluna ensaios_extras na tabela evento
Execute: python atualizar_banco.py
"""

import sqlite3
import os

def atualizar_banco():
    """Adiciona a coluna ensaios_extras na tabela evento"""
    
    db_path = 'instance/fotografia.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        print("Execute primeiro: python app.py")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(evento)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        
        if 'ensaios_extras' in colunas:
            print("✅ Coluna 'ensaios_extras' já existe!")
        else:
            # Adicionar a nova coluna
            cursor.execute("ALTER TABLE evento ADD COLUMN ensaios_extras VARCHAR(100) DEFAULT 'Nenhum'")
            
            # Atualizar registros existentes
            cursor.execute("UPDATE evento SET ensaios_extras = 'Nenhum' WHERE ensaios_extras IS NULL")
            
            conn.commit()
            print("✅ Coluna 'ensaios_extras' adicionada com sucesso!")
            print("✅ Registros existentes atualizados com valor padrão 'Nenhum'")
        
        conn.close()
        print("\n🚀 Banco de dados atualizado! Agora você pode executar o sistema.")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")

if __name__ == "__main__":
    print("🔧 ATUALIZANDO BANCO DE DADOS")
    print("=" * 40)
    atualizar_banco()