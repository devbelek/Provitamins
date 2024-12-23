FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Настраиваем DNS
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf

WORKDIR /vitamins-backend

# Установка минимально необходимых системных пакетов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        netcat \
        python3-dev \
        gcc \
        libc-dev \
        linux-headers-amd64 \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Python пакетов
RUN pip install --no-cache-dir pip setuptools wheel

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

# Копируем скрипты и делаем их исполняемыми
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

# Копируем проект
COPY . /vitamins-backend/