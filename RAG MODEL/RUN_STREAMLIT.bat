@echo off
title Starting Streamlit Dual AI Dashboard
echo =========================================================
echo Starting Streamlit Dual AI Engine (RAG Model + AI Agent)
echo =========================================================
cd /d "%~dp0"
echo Launching Streamlit...
streamlit run app.py
pause
