@echo off
title Starting PixelCore Dual AI Web Interface
echo =========================================================
echo Starting PixelCore Dual AI Engine (RAG Model + AI Agent)
echo =========================================================
cd /d "%~dp0frontend"
echo Starting Vite Dev Server...
call npm run dev
pause
