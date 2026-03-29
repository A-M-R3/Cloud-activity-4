from app.files.persistence.minio_repository import MinioRepository

minio_repository = MinioRepository()

def get_minio_repository() -> MinioRepository:
    return minio_repository