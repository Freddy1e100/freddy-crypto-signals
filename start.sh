#!/bin/bash

# Устанавливаем порт, который требует Render
export PORT=${PORT:-8501}

# Запускаем Streamlit с привязкой к внешнему порту
streamlit run main.py --server.port=$PORT --server.enableCORS=false
