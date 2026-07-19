FROM python:3.11-slim
WORKDIR /app
COPY requirements-backend.txt .
RUN pip install -r requirements-backend.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]