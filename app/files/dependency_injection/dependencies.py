from app.files.persistence.minio_repository import MinioFileStorageService
from app.files.domain.controllers import (
    UploadFileContentController,
    DownloadFileController,
    DeleteFileController,
    MergeFilesController
)

file_storage_service = MinioFileStorageService()

upload_file_controller = UploadFileContentController(file_storage_service)
download_file_controller = DownloadFileController(file_storage_service)
delete_file_controller = DeleteFileController(file_storage_service)
merge_files_controller = MergeFilesController(file_storage_service)