# Используем официальный образ Python в качестве базового
FROM python:3.13.3

# Установите необходимые переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей, если они есть
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код вашего бота в контейнер
COPY . /app/

# Определяем команду для запуска бота
CMD ["python", "bot.py"]