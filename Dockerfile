FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Настройка pip для работы с зеркалами
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ENV PIP_TRUSTED_HOST=mirrors.aliyun.com

WORKDIR /vitamins-backend

# Установка зависимостей
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копирование скриптов и настройка прав
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

# Копирование остальных файлов проекта
COPY . /vitamins-backend/