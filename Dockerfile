# Použij oficiální Python image
FROM python:3.10-slim

WORKDIR /app

# Závislosti
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Zbytek aplikace (včetně app.py, migrations, atd.)
COPY . .

# SQLite databáze bude v /app (implicitně)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Volitelně – můžeš si nastavit vlastní proměnnou pro DB URL
# Default je SQLite soubor v /app/app.db
ENV DATABASE_URL=sqlite:////app/app.db

# Entry point, kde se nejdřív spustí migrace a pak server
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
