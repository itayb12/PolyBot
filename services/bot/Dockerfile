FROM python:3.9-slim-bullseye
WORKDIR /app
ENV APP_PATH=/var/lib/jenkins/workspace/BotBuild/services
#ENV APP_PATH=/var/lib/jenkins/workspace/BotBuild/services
COPY . .
RUN pip install -r $APP_PATH/requirements.txt

CMD ["python3", "APP_PATH/bot/app.py"]