FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY requirements-pipeline.txt .
RUN pip install --no-cache-dir -r requirements-pipeline.txt

COPY . .

# One command: generate -> validate -> split -> baselines -> train -> register -> verify
CMD ["python", "-m", "src.pipeline.run_all"]
