FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

WORKDIR /vitamins-backend

# Установка системных зависимостей для Pillow и других пакетов
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip install --upgrade pip

# Устанавливаем Pillow отдельно
RUN pip install Pillow==10.3.0

# Копируем wheels и requirements
COPY wheels /wheels
COPY requirements.txt .

# Создаем временный requirements без Pillow
RUN grep -v "Pillow" requirements.txt > requirements_no_pillow.txt

# Устанавливаем остальные пакеты из wheels
RUN pip install --no-index --find-links=/wheels -r requirements_no_pillow.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

COPY . /vitamins-backend/