@echo off
echo ========================================
echo   Configurando Git e GitHub
echo ========================================
echo.

REM Verificar se o Git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Git nao encontrado!
    echo Por favor, instale o Git: https://git-scm.com/download/windows
    pause
    exit /b 1
)

echo 1. Inicializando repositorio Git...
git init

echo 2. Adicionando arquivos...
git add .

echo 3. Fazendo primeiro commit...
git commit -m "Primeiro commit: Sistema de gestao para fotografia e storymaker"

echo.
echo ========================================
echo   PROXIMOS PASSOS:
echo ========================================
echo.
echo 1. Va para: https://github.com/new
echo 2. Crie um repositorio com o nome: fotografia-sistema
echo 3. NAO inicialize com README, .gitignore ou licenca
echo 4. Copie a URL do repositorio (ex: https://github.com/SEU_USUARIO/fotografia-sistema.git)
echo 5. Execute os comandos abaixo substituindo SEU_USUARIO:
echo.
echo    git remote add origin https://github.com/SEU_USUARIO/fotografia-sistema.git
echo    git branch -M main
echo    git push -u origin main
echo.
pause