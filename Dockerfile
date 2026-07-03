FROM python:3.11-slim

# Lean, reproducible, and container-friendly Streamlit defaults so the
# dashboard is reachable from outside the container.
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

# pyproject readme points at README.md, so it is needed at build time.
COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install . \
    && useradd --create-home --uid 1000 kairos

USER kairos

EXPOSE 8501

CMD ["kairos", "dashboard"]
