from os import getenv

from dotenv import load_dotenv
from storages.backends.s3boto3 import S3Boto3Storage

load_dotenv(override=True)


class PublicMediaStorage(S3Boto3Storage):
    access_key = getenv('STORAGE_MEDIA_ACCESS_KEY_ID', 'access_key')
    secret_key = getenv('STORAGE_MEDIA_SECRET_ACCESS_KEY', 'secret_key')
    bucket_name = getenv('STORAGE_MEDIA_STORAGE_BUCKET_NAME', 'lms-learn-app')
    endpoint_url = getenv(
        'STORAGE_MEDIA_S3_ENDPOINT_URL',
        'https://fra1.digitaloceanspaces.com'
        )
    custom_domain = getenv('STORAGE_MEDIA_S3_CUSTOM_DOMAIN', None)
    region_name = getenv('STORAGE_MEDIA_S3_REGION_NAME', 'fra1')
    location = getenv('STORAGE_MEDIA_LOCATION', 'media')
    object_parameters = {
        'CacheControl': 'max-age=86400'
        }
    file_overwrite = True
    querystring_auth = False
    default_acl = 'public-read'


class PublicStaticStorage(S3Boto3Storage):
    access_key = getenv('STORAGE_STATIC_ACCESS_KEY_ID', 'access_key')
    secret_key = getenv('STORAGE_STATIC_SECRET_ACCESS_KEY', 'secret_key')
    bucket_name = getenv('STORAGE_STATIC_STORAGE_BUCKET_NAME', 'lms-learn-app')
    endpoint_url = getenv(
        'STORAGE_STATIC_S3_ENDPOINT_URL',
        'https://fra1.digitaloceanspaces.com'
        )
    custom_domain = getenv('STORAGE_STATIC_S3_CUSTOM_DOMAIN', None)
    region_name = getenv('STORAGE_STATIC_S3_REGION_NAME', 'fra1')
    location = getenv('STORAGE_STATIC_LOCATION', 'static')
    object_parameters = {
        'CacheControl': 'max-age=86400'
        }
    file_overwrite = True
    querystring_auth = False
    default_acl = 'public-read'
