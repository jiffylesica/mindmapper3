# Multi-stage build (smaller final image)
FROM python:3.11-slim as builder

WORKDIR /app
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --user --no-cache-dir -e .

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/

ENV PATH=/root/.local/bin:$PATH
ENV FLASK_APP=src/mindmapper/web/app.py

EXPOSE 5000

# Use non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "mindmapper.web.app:app"]