import time
from yt_dlp import YoutubeDL
from loguru import logger
import boto3
import botocore
import os


def search_download_youtube_video(video_name, num_results=1):
    """
    This function downloads the first num_results search results from Youtube
    :param video_name: string of the video name
    :param num_results: integer representing how many videos to download
    :return: list of paths to your downloaded video files
    """
    #with YoutubeDL() as ydl:
    #    videos = ydl.extract_info(f"ytsearch{num_results}:{video_name}", download=True)['entries']
    #return [ydl.prepare_filename(video) for video in videos]

    with YoutubeDL() as ydl:
        videos = ydl.extract_info(f"ytsearch{num_results}:{video_name}", download=False)['entries']
        for video in videos:
            key = "dir-1/"
            file_name = video['title'] + " [" + video['id'] + "].mp4"
            file_name = file_name.replace('|', "")
            key_value = key + file_name
            print(key_value)
            s3_res = boto3.resource('s3')
            s3 = boto3.client('s3')
            try:
                s3_res.Object('zoharnpolys3', key_value).load()
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                    video_url = video['webpage_url']
                    ydl.extract_info(video_url, download=True)
                    files = os.listdir('.')
                    for f in files:
                        if '.mp4' in f:
                            newname = file_name
                            os.rename(f, newname)
                    s3.upload_file(Bucket='zoharnpolys3', Key=key_value, Filename=file_name)
                    os.remove(file_name)
                else:
                    print("Something else has gone wrong.")
                    raise
            else:
                print("The object does exist.")

    return [ydl.prepare_filename(video) for video in videos]



def calc_backlog_per_instance(sqs_queue_client, asg_client, asg_group_name):
    while True:
        msgs_in_queue = int(sqs_queue_client.attributes.get('ApproximateNumberOfMessages'))
        asg_size = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_group_name])['AutoScalingGroups'][0]['DesiredCapacity']

        if msgs_in_queue == 0:
            backlog_per_instance = 0
        elif asg_size == 0:
            backlog_per_instance = 99
        else:
            backlog_per_instance = msgs_in_queue / asg_size

        logger.info(f'backlog per instance: {backlog_per_instance}')

        # TODO send the backlog_per_instance metric to cloudwatch

        time.sleep(60)
