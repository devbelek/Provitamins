FROM python:3.9

# stdder stddin
ENV PYTHONUNBUFFERED=1
# python dont create .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Dockerfile
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

WORKDIR /vitamins-backend

# Обновляем pip
RUN pip install --upgrade pip

# Копируем локальный кэш пакетов и requirements.txt
COPY pip-packages /pip-packages
COPY requirements.txt ./

# Устанавливаем пакеты из локального кэша
RUN pip install --no-index --find-links=/pip-packages -r requirements.txt

# Копируем скрипты и делаем их исполняемыми
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

# Копируем все остальные файлы проекта
COPY . /vitamins-backend/