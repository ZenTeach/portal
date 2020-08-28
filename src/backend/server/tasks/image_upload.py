import os
from hashlib import md5
from pathlib import Path

import boto3
from boto3 import client
from celery.utils.log import get_task_logger
from server import celery

# from server.models import ClassQuiz, ClassQuizStatus


BUCKET = os.environ.get('AWS_QUESTIONS_BUCKET')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
REGION = "eu-west-2"

logger = get_task_logger(__name__)
s3 = boto3.resource('s3')
s3_client = client('s3')
bucket = s3.Bucket(BUCKET)


@celery.task(bind=True)
def upload_image_to_s3(self, image_location):
    image_path = Path(image_location)
    if not image_path.exists():
        raise Exception("Image file not found.")
    image_name = image_path.name
    key = "{}_{}".format(image_name, md5(image_path.name.encode('utf-8')).hexdigest())  # nosec
    # mimeinfo = guess_type(image_path, strict=True)
    # res = s3.Bucket(BUCKET).put_object(  # noqa
    #             ACL='public-read',
    #             Body=image_path.read_bytes(),
    #             Key=key,
    #             ContentType=mimeinfo[0])
    s3_client.upload_file(image_path, BUCKET, key, ExtraArgs={'ACL': 'public-read'})

    url = "https://{}.s3.{}.amazonaws.com/{}".format(BUCKET, REGION, key)
    return url


@celery.task(bind=True)
def delete_image_from_s3(self, o_identifier):
    deleted_object = s3.Bucket(BUCKET).delete_objects(
        Delete={
            'Objects': [
                {
                    'Key': o_identifier
                }
            ]
        }
    )

    return deleted_object


@celery.task(bind=True)
def delete_from_tmp_image_directory(dir):
    pass


@celery.task(bind=True)
def refresh_image_to_s3(image_dir, image_url):
    pass

# @celery.task(bind=True)
# def upload_image_to_s3(image_dir):
#     pass
