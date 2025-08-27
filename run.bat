@echo off
SETLOCAL
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
pause
