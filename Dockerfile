FROM python:3.9

# stdder stddin
ENV PYTHONUNBUFFERED=1
# python dont create .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Dockerfile
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

WORKDIR /vitamins-backend

# Добавляем эти строки для настройки pip
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf && \
    pip config set global.index-url https://pypi.org/simple/ && \
    pip config set global.trusted-host pypi.org && \
    pip config set global.trusted-host files.pythonhosted.org

RUN pip install --upgrade pip --no-cache-dir

COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

COPY . /vitamins-backend/