FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .
COPY .gitignore .
COPY src/ src/

RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install .

EXPOSE 8000
CMD ["uvicorn", "chatbot_platform.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
