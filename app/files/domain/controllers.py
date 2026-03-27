from app.files.domain.interfaces import FileStorageInterface
import os

class UploadFileContentController:
    def __init__(self, file_storage_service: FileStorageInterface):
        self.file_storage_service = file_storage_service

    async def __call__(self, file_id: str, local_file_path: str) -> str:
        remote_path = f"files/{file_id}"
        
        await self.file_storage_service.put_file(
            local_path=local_file_path, 
            remote_identifier=remote_path
        )
        
        
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            
        return remote_path


class DownloadFileController:
    def __init__(self, file_storage_service: FileStorageInterface):
        self.file_storage_service = file_storage_service

    async def __call__(self, file_id: str, local_folder: str = "/tmp") -> str:
        remote_path = f"files/{file_id}"
        
        local_path = await self.file_storage_service.get_file(
            remote_path=remote_path, 
            local_folder=local_folder
        )
        return local_path


class DeleteFileController:
    def __init__(self, file_storage_service: FileStorageInterface):
        self.file_storage_service = file_storage_service
        # self.file_repository = file_repository

    async def __call__(self, file_id: str) -> None:
        remote_path = f"files/{file_id}"
        
        await self.file_storage_service.remove_file(remote_identifier=remote_path)
        


class MergeFilesController:
    def __init__(self, file_storage_service: FileStorageInterface):
        self.file_storage_service = file_storage_service

    async def __call__(self, file_id_1: str, file_id_2: str, new_file_id: str) -> str:
        local_path_1 = await self.file_storage_service.get_file(f"files/{file_id_1}", "/tmp")
        local_path_2 = await self.file_storage_service.get_file(f"files/{file_id_2}", "/tmp")
        
        merged_local_path = f"/tmp/{new_file_id}.pdf"
        
        from PyPDF2 import PdfMerger
        merger = PdfMerger()
        merger.append(local_path_1)
        merger.append(local_path_2)
        merger.write(merged_local_path)
        merger.close()
        
        remote_path = f"files/{new_file_id}"
        await self.file_storage_service.put_file(merged_local_path, remote_path)
        
        os.remove(local_path_1)
        os.remove(local_path_2)
        os.remove(merged_local_path)
        
        return remote_path