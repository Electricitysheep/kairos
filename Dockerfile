FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY notebooks/ ./notebooks/
COPY examples/ ./examples/

RUN pip install --no-cache-dir -e .

EXPOSE 8501

CMD ["kairos", "dashboard"]
