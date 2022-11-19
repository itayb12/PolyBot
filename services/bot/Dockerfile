FROM python:3.9-slim-bullseye
WORKDIR /app
#ENV APP_PATH=/var/lib/jenkins/workspace/BotBuild/services/bot
#ENV APP_PATH=/var/lib/jenkins/workspace/BotBuild/services
COPY . .
RUN pip install -r /var/lib/jenkins/workspace/BotBuild/services/bot/requirements.txt

CMD ["python3", "/var/lib/jenkins/workspace/BotBuild/services/bot/app.py"]