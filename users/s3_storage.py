import os
from storages.backends.s3boto3 import S3Boto3Storage


class S3_ProfileImage_Storage(S3Boto3Storage):
    bucket_name = os.environ.get("AWS_BUCKET_NAME")
    location = 'profile_images'
