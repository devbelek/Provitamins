FROM python:3.9
# stdder stddin
ENV PYTHONUNBUFFERED=1
# python dont create .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Dockerfile
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

WORKDIR /vitamins-backend


RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint_bot.sh /entrypoint_bot.sh
RUN chmod +x /entrypoint_bot.sh

COPY . /vitamins-backend/
