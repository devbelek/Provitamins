FROM python:3.9

# stdder stddin
ENV PYTHONUNBUFFERED=1
# python dont create .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Dockerfile
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

WORKDIR /vitamins-backend

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    postgresql-client \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip install --upgrade pip

# Устанавливаем Pillow напрямую
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