FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Устанавливаем переменные окружения для pip
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ENV PIP_TRUSTED_HOST=mirrors.aliyun.com

WORKDIR /vitamins-backend

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .

# Обновляем pip и устанавливаем пакеты
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем файлы проекта
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . /vitamins-backend/