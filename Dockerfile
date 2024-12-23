FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

WORKDIR /vitamins-backend

# Копируем предварительно скачанные wheels
COPY wheels /wheels
COPY requirements.txt .

# Устанавливаем пакеты из локальных wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

COPY . /vitamins-backend/