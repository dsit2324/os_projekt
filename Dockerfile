# Oficiální Python image
FROM python:3.10-slim

WORKDIR /app

# Závislosti
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Zbytek aplikace
COPY . .

# SQLite databáze bude v /app/dbdata/app.db
# (máš tam složku dbdata v repu, tak ji budeme používat)
RUN mkdir -p /app/dbdata

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# URL databáze – SQLite soubor v /app/dbdata/app.db
ENV DATABASE_URL=sqlite:////app/dbdata/app.db

# entrypoint skript
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
