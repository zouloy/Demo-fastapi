FROM python:3.11-slim

WORKDIR /app

# Vi kopierar kraven först
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Här kopierar vi allt (main.py, database.db, .env) till /app
COPY ./app . 

# Nu ligger main.py direkt i /app/ och detta fungerar:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8800"]