from minio import Minio
from app.config import minio_settings

class MinioRepository:
    def __init__(self):
        self.client = Minio(
            minio_settings.endpoint,
            access_key=minio_settings.access_key,
            secret_key=minio_settings.secret_key,
            secure=minio_settings.secure
        )
        self.bucket_name = minio_settings.bucket_name

    def upload_file(self, local_path: str, remote_path: str):
        self.client.fput_object(self.bucket_name, remote_path, local_path)

    def download_file(self, remote_path: str, local_path: str):
        self.client.fget_object(self.bucket_name, remote_path, local_path)

    def delete_file(self, remote_path: str):
        self.client.remove_object(self.bucket_name, remote_path)