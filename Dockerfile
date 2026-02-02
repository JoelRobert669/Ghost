FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000
EXPOSE 6723

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6723"]
