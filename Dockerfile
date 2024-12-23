FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

WORKDIR /vitamins-backend

# Установка Python пакетов напрямую из зеркала
RUN pip install --no-cache-dir pip setuptools wheel

# Копируем requirements и устанавливаем зависимости через зеркало
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# Копируем скрипты и делаем их исполняемыми
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

# Копируем проект
COPY . /vitamins-backend/