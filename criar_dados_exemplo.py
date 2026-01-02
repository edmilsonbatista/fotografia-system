from app import app, db, Evento, Transacao
from datetime import datetime, date, timedelta

def criar_dados_exemplo():
    """Inicializa o banco de dados sem dados de exemplo"""
    
    with app.app_context():
        # Limpar dados existentes e criar tabelas
        db.drop_all()
        db.create_all()
        
        print("Banco de dados inicializado com sucesso!")
        print("\nSistema pronto para receber dados via importação.")
        print("\nExecute 'python app.py' para iniciar o sistema!")

if __name__ == '__main__':
    criar_dados_exemplo()