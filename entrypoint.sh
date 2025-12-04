#!/bin/sh
# Spustit migrace (vytvoří/aktualizuje DB podle modelů)
flask db upgrade

# Nastartovat Flask aplikaci
flask run --host=0.0.0.0 --port=5000
