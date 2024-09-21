from minio import Minio, S3Error
from typing import Any

import io
import logging


from app.core.config import settings


class MinioClient:

    def __init__(self, endpoint, access_key, secret_key, secure=True):
        try:
            self.client = Minio(endpoint, access_key, secret_key, secure=secure)
            self._endpoint_url = settings.MINIO_ENDPOINT
            logging.info(f"Connected to Minio at {endpoint}")
        except Exception as e:
            logging.error(f"Failed to connect to Minio: {e}")
            raise e

    def create_bucket(self, bucket_name: str) -> str:
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logging.info(f"Bucket '{bucket_name}' created.")
            else:
                logging.info(f"Bucket '{bucket_name}' already exists.")
            return bucket_name
        except S3Error as e:
            logging.error(f"Failed to create or access bucket '{bucket_name}': {e}")
            raise e

    def upload_file(self, bucket_name: str, destination_file: str, source_file: Any, content_type: str = None):
        try:
            if isinstance(source_file, str):
                source_file = io.BytesIO(source_file.encode('utf-8'))
                length = len(source_file.getvalue())
            elif hasattr(source_file, 'read'):
                source_file.seek(0, io.SEEK_END)
                length = source_file.tell()
                source_file.seek(0, io.SEEK_SET)
            else:
                raise ValueError("Invalid source_file type")

            self.client.put_object(
                bucket_name,
                destination_file,
                data=source_file,
                length=length,
                content_type=content_type
            )
            logging.info(f"File '{destination_file}' uploaded to bucket '{bucket_name}'.")
        except S3Error as e:
            logging.error(f"Failed to upload file '{destination_file}' to bucket '{bucket_name}': {e}")
            raise e
        except ValueError as e:
            logging.error(f"Invalid source file type for '{destination_file}': {e}")
            raise e

    def get_content(self, bucket_name: str, object_name: str):
        try:
            content = self.client.get_object(bucket_name, f"{object_name}/content.json")
            logging.info(f"Retrieved content from '{object_name}' in bucket '{bucket_name}'.")
            return content
        except S3Error as e:
            logging.error(f"Failed to retrieve content from '{object_name}' in bucket '{bucket_name}': {e}")
            raise e

    def get_object_url(self, bucket_name: str, object_name: str) -> str:
        try:
            url = f"{self._endpoint_url}/{bucket_name}/{object_name}"
            logging.info(f"Generated URL for object '{object_name}' in bucket '{bucket_name}': {url}")
            return url
        except Exception as e:
            logging.error(f"Failed to generate URL for object '{object_name}' in bucket '{bucket_name}': {e}")
            raise e

    def list_files(self, bucket_name: str, prefix: str) -> list:
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            files = [obj.object_name for obj in objects]
            logging.info(f"Listed files in bucket '{bucket_name}' with prefix '{prefix}': {files}")
            return files
        except S3Error as e:
            logging.error(f"Failed to list files in bucket '{bucket_name}' with prefix '{prefix}': {e}")
            raise e


minio_client = MinioClient(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)
