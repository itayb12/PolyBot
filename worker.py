import json
import os
import string
import time
import boto3
import botocore
from loguru import logger
from utils import search_download_youtube_video
from yt_dlp import YoutubeDL
import telegram
my_bucket = "zoharnpolys3"


def fix_file_name(file_name):
    file_name = str(file_name)
    for char in string.punctuation:
        file_name = file_name.replace(char, "")

    return file_name


def check_bucket_for_file(key, file_name):
    s3_res = boto3.resource('s3')
    s3 = boto3.client('s3')

    try:
        s3_res.Object(my_bucket, key + file_name).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
    return True


def upload_file_to_bucket(key, file_full_path):
    #s3_res = boto3.resource('s3')
    s3 = boto3.client('s3')

    s3.upload_file(Bucket=my_bucket, Key=key+file_full_path, Filename=file_full_path)
    #os.remove(file_full_path)


def download_from_bucket_and_send(key, file_path, bot, chatid, videoid):
    s3 = boto3.client('s3')

    response = s3.head_object(Bucket = my_bucket, Key = key + file_path)
    size = response['ContentLength']
    if size < 1024 * 1024 * 50:
        s3.download_file(my_bucket, key + file_path, file_path)
        bot.send_video(chatid, video=open(file_path, 'rb'))
        os.remove(file_path)
    else:
        bot.send_message(chat_id=chatid, text="youtube.com/watch?v=" + videoid)


def process_msg(msg, chatid):
    key = "Videos/"
    with open('.telegramToken') as f:
        _token = f.read()
    bot = telegram.Bot(token=_token)

    if msg == "/start":
        bot.send_message(chat_id=chatid, text="Welcome to our bot! please type in your video request")
        return None

    with YoutubeDL() as ydl:
        videos = ydl.extract_info(f"ytsearch{1}:{msg}", download=False)['entries']

        if len(videos) == 0:
            bot.send_message(chat_id=chatid, text="The selected video was not found.")
        else:
            for video in videos:
                # check if video is live, don't upload to s3 and send link with the video
                if video['is_live'] == True:
                    bot.send_message(chat_id=chatid, text="youtube.com/watch?v=" + video['id'])
                else:
                    # remove chars from file name so file upload to s3 won't crash
                    file_name = fix_file_name(video['title']) + " [" + video['id'] + "].mp4"
                    # check "filesize" to determine the following conditions:
                    if "filesize" not in video:
                        video['filesize'] = video['filesize_approx']
                    if "filesize" in video:
                        if video["filesize"] is None:
                            video["filesize"] = 3100000000
                        # if "filesize" > 3GB don't download the video and don't upload to s3, send video link instead
                        if video['filesize'] > 1024 * 1024 * 1024 * 3:
                            bot.send_message(chat_id=chatid, text="youtube.com/watch?v=" + video['id'])
                        # if "filesize" > 50MB: check if exist in s3 already, download video if not and upload it to s3, send video link
                        elif video['filesize'] > 1024 * 1024 * 50:
                            if check_bucket_for_file(key, file_name) == True:
                                bot.send_message(chat_id=chatid, text="youtube.com/watch?v=" + video['id'])
                            else:
                                paths = search_download_youtube_video(msg)

                                for path in paths:
                                    os.rename(path, file_name)
                                    bot.send_message(chat_id=chatid, text="youtube.com/watch?v=" + video['id'])
                                    upload_file_to_bucket(key, file_name)
                                    os.remove(file_name)

                        else:
                            # if "filesize" < 50MB: check if exist in s3 already, download video if not and upload it to s3, send video back
                            if check_bucket_for_file(key, file_name) == True:
                                download_from_bucket_and_send(key, file_name, bot, chatid, video['id'])

                            else:
                                paths = search_download_youtube_video(msg)

                                for path in paths:
                                    os.listdir('.')
                                    os.rename(path, file_name)
                                    upload_file_to_bucket(key, file_name)
                                    bot.send_video(chatid, video=open(file_name, 'rb'))
                                    os.remove(file_name)


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

                # delete message from the queue after it was handled
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
