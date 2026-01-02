@echo off
echo ========================================
echo   Sistema de Gestao - Fotografia Pro
echo ========================================
echo.
echo Iniciando o sistema...
echo.

REM Verificar se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.7 ou superior.
    pause
    exit /b 1
)

REM Verificar se as dependências estão instaladas
python -c "import flask, flask_sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERRO: Falha ao instalar dependencias!
        pause
        exit /b 1
    )
)

REM Verificar se o banco de dados existe
if not exist "instance\fotografia.db" (
    echo Criando banco de dados com dados de exemplo...
    python criar_dados_exemplo.py
)

echo.
echo ========================================
echo   Sistema iniciado com sucesso!
echo ========================================
echo.
echo Acesse: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar o sistema
echo.

REM Iniciar a aplicação
python app.py

pause