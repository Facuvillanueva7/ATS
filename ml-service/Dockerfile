FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false
COPY . .
RUN poetry install --no-interaction --no-ansi
EXPOSE 8081
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
