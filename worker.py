import json
import os
import time
import boto3
import botocore
from loguru import logger
from utils import search_download_youtube_video
import telegram
# from secrets import access_key, secret_access_key


def process_msg(msg, chatid):
    paths = search_download_youtube_video(msg)
    for path in paths:
        s3 = boto3.client('s3')
        with open('.telegramToken') as f:
            _token = f.read()
        bot = telegram.Bot(token=_token)
        strList = path.split("[")
        videoID = strList[len(strList) - 1].split("]", 1)
        bot.send_message(chat_id=chatid, text="youtube.com/watch?v=" + videoID[0])
        #bot.send_video(chat_id=chatid, video=open(path, 'rb'), supports_streaming=True)
        #s3.upload_file(Bucket='zoharnpolys3', Key="dir-1/" + path, Filename=path)


def main():
    while True:
        logger.info("waiting for new request")
        try:
            messages = queue.receive_messages(
                MessageAttributeNames=['All'],
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )

            for msg in messages:
                # logger.info("hey this is chat id: " + msg.message_attributes.get('chat_id').get('StringValue'))
                logger.info(f'processing message {msg}')
                process_msg(msg.body, msg.message_attributes.get('chat_id').get('StringValue'))

                # delete message from the queue after is was handled
                response = queue.delete_messages(Entries=[{
                    'Id': msg.message_id,
                    'ReceiptHandle': msg.receipt_handle
                }])
                if 'Successful' in response:
                    logger.info(f'msg {msg} has been handled successfully')

        except botocore.exceptions.ClientError as err:
            logger.exception(f"Couldn't receive messages {err}")
            time.sleep(10)


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    sqs = boto3.resource('sqs', region_name=config.get('aws_region'))
    queue = sqs.get_queue_by_name(QueueName=config.get('bot_to_worker_queue_name'))

    main()
