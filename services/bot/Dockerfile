FROM python:3.9-slim-bullseye
WORKDIR /app
#ENV APP_PATH=/var/lib/jenkins/workspace/BotBuild/services/bot
#ENV APP_PATH=/var/lib/jenkins/workspace/BotBuild/services
COPY . .
RUN pip install -r requirements.txt

CMD ["python3", "app.py"]