FROM python:3.9-slim-bullseye
WORKDIR /app
ENV APP_PATH=services/bot
COPY . .
RUN pip install -r $APP_PATH/requirements.txt

CMD ["python3", "services/bot/app.py"]

#FROM python:3.9-slim-bullseye
#WORKDIR /app
#ENV APP_PATH=/var/lib/jenkins/workspace/BotBuild/services/bot
#ENV APP_PATH=/var/lib/jenkins/workspace/BotBuild/services
#COPY . .
#RUN pip install -r requirements.txt
#$45664655
#
#CMD ["python3", "app.py"]