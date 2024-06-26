# Указываем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /bot

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения в контейнер
COPY . /bot

# Указываем команду для запуска приложения
CMD ["python", "bot.py"]