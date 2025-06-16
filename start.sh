#!/bin/bash
export PORT=${PORT:-8501}
streamlit run main.py --server.port=$PORT --server.enableCORS=false
