FROM python:3.9

# stdder stddin
ENV PYTHONUNBUFFERED=1
# python dont create .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Dockerfile
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Настраиваем DNS
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf

WORKDIR /vitamins-backend

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    netcat \
    postgresql \
    build-essential \
    python3-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip и устанавливаем базовые инструменты
RUN pip install --upgrade pip wheel setuptools

# Устанавливаем Pillow
RUN pip install Pillow==10.3.0

# Копируем локальный кэш пакетов и requirements.txt
COPY pip-packages /pip-packages
COPY requirements.txt ./

# Создаем временный requirements без Pillow
RUN grep -v "Pillow" requirements.txt > requirements_no_pillow.txt

# Устанавливаем остальные пакеты из локального кэша
RUN pip install --no-index --find-links=/pip-packages -r requirements_no_pillow.txt

# Копируем скрипты и делаем их исполняемыми
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

# Копируем все остальные файлы проекта
COPY . /vitamins-backend/