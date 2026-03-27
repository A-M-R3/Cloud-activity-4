from minio import Minio
from app.files.domain.interfaces import FileStorageInterface
from app.config import minio_settings

class MinioFileStorageService(FileStorageInterface):
    def __init__(self):
        self.client = Minio(
            minio_settings.endpoint,
            access_key=minio_settings.access_key,
            secret_key=minio_settings.secret_key,
            secure=minio_settings.secure
        )
        self.bucket_name = minio_settings.bucket_name

    async def put_file(self, local_path: str, remote_identifier: str):
        """Upload a file to storage"""
        self.client.fput_object(
            bucket_name=self.bucket_name, 
            object_name=remote_identifier, 
            file_path=local_path
        )
        return remote_identifier

    async def get_file(self, remote_path: str, local_folder: str):
        """Download a file from storage"""
        filename = remote_path.split("/")[-1]
        local_path = f"{local_folder}/{filename}"
        
        self.client.fget_object(
            bucket_name=self.bucket_name, 
            object_name=remote_path, 
            file_path=local_path
        )
        return local_path

    async def remove_file(self, remote_identifier: str):
        """Delete a file from storage"""
        self.client.remove_object(
            bucket_name=self.bucket_name, 
            object_name=remote_identifier
        )