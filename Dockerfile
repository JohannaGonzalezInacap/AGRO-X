# Fase 10 (RUTA.md): imagen de contenedor, sin usuario root.
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .

RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Aplica migraciones antes de levantar el servidor. Render (y la mayoría de las plataformas
# de contenedores) inyectan el puerto real en $PORT; 8000 es solo el valor por defecto local.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
