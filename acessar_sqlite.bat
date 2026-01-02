@echo off
echo ========================================
echo   ACESSO DIRETO AO BANCO SQLITE
echo ========================================
echo.

REM Verificar se o SQLite está instalado
sqlite3 -version >nul 2>&1
if errorlevel 1 (
    echo ERRO: SQLite3 nao encontrado!
    echo Baixe em: https://sqlite.org/download.html
    pause
    exit /b 1
)

echo Abrindo banco de dados...
echo.
echo Comandos uteis:
echo   .tables          - Listar tabelas
echo   .schema evento   - Ver estrutura da tabela evento
echo   .schema transacao - Ver estrutura da tabela transacao
echo   .quit            - Sair
echo.

sqlite3 instance\fotografia.db