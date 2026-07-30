@echo off
chcp 65001 >nul
title VOGUE - Terminal System
color 0F
mode con: cols=75 lines=25

echo.
echo  __      __  ____    _____  _    _  ______
echo  \ \    / / / __ \  / ____^| ^|  ^| ^| ^|  ____^|
echo   \ \  / / ^| ^|  ^| ^|^| ^|  __  ^|  ^| ^| ^| ^|__
echo    \ \/ /  ^| ^|  ^| ^|^| ^| ^|_ ^| ^|  ^| ^| ^|  __^|
echo     \  /   ^| ^|__^| ^|^| ^|__^| ^| ^|__^| ^| ^| ^|____
echo      \/     \____/  \_____^| \____/  ^|______^|
echo.
echo  ================================================
echo             INICIANDO SISTEMA VOGUE
echo  ================================================
echo.
echo  [+] Carregando dependencias...
echo  [+] Conectando a rede do Discord...
echo.

python core_python\main.py

echo.
echo  [!] O sistema foi encerrado ou encontrou um erro.
echo.
pause
