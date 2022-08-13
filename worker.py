import json
import os
import time
import boto3
import botocore
from loguru import logger
from utils import search_download_youtube_video
# from secrets import access_key, secret_access_key


def process_msg(msg):

    paths = search_download_youtube_video(msg)

    #for path in paths:
    #    s3 = boto3.client('s3')
    #    s3_res = boto3.resource('s3')
    #    try:
    #        s3_res.Object('zoharnpolys3', "dir-1/" + path).load()
    #    except botocore.exceptions.ClientError as e:
    #        if e.response['Error']['Code'] == "404":
    #            print("The object does not exist.")
    #            s3.upload_file(Bucket='zoharnpolys3', Key="dir-1/" + path, Filename=path)
    #        else:
    #            print("Something else has gone wrong.")
    #            raise
    #    else:
    #        print("The object does exist.")
        #os.remove(path)

    #downloaded_file = search_download_youtube_video(msg)

    #client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_access_key)
#
 #   for file in os.listdir():
  #      if '.mp4' in file:
   #         upload_file_bucket = 'zoharnpolys3'
    #        upload_file_key = 'Videosboto3/' + str(file)
     #       client.upload_file(file, upload_file_bucket, upload_file_key)


def main():
    while True:
        try:
            messages = queue.receive_messages(
                MessageAttributeNames=['All'],
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )
            for msg in messages:
                logger.info(f'processing message {msg}')
                process_msg(msg.body)

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
