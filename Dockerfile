FROM python:3.11-slim

WORKDIR /app

# Sabse pehle requirements install karo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saari files copy karo
COPY . .

# Port Railway automatically set karega, hum sirf 0.0.0.0:8000 use karenge
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 app:app
