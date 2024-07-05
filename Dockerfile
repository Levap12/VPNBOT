# Используйте базовый образ Python
FROM python:3.9-slim

# Установите зависимости
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте все файлы в контейнер
COPY . .

# Убедитесь, что переменные окружения будут загружены
ENV PYTHONPATH=/app

# Запустите FastAPI приложение
CMD ["uvicorn", "fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
