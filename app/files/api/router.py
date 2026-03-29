from typing import Optional
import httpx
import uuid
from pypdf import PdfMerger
import os

from fastapi import APIRouter, Header, HTTPException, Body, File, UploadFile, Depends
from pydantic import BaseModel
from app.files.dependency_injection.dependencies import get_minio_repository
from app.files.persistence.minio_repository import MinioRepository

router = APIRouter()

class User(BaseModel):
    username: str
    address: Optional[str] = None

class FileBusinesObject(BaseModel):
    id: int
    user: User
    title: str
    author: str
    path: Optional[str] = None

id_counter = 0
files_database = {}

async def introspect(token: str) -> User:
    url = "http://localhost:8000/introspect"
    headers = {
        "accept": "application/json",
        "auth": token
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return User(**response.json())

def check_file_ownership(id: int, user: User):
    if id not in files_database:
        raise HTTPException(status_code=404, detail="File not found")
    file = files_database[id]
    if user.username != file.user.username:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return file

class PostFilesMerge(BaseModel):
    file_id_1: int
    file_id_2: int

@router.post("/merge")
async def merge_files(token: str = Header(alias="auth"), input: PostFilesMerge = Body(), minio_repo: MinioRepository = Depends(get_minio_repository)) -> dict[str, str]:
    user = await introspect(token=token)
    file_1 = check_file_ownership(input.file_id_1, user)
    file_2 = check_file_ownership(input.file_id_2, user)
    
    file_path_1 = file_1.path
    file_path_2 = file_2.path
    
    temp_1 = f"/tmp/temp_1_{uuid.uuid4()}.pdf"
    temp_2 = f"/tmp/temp_2_{uuid.uuid4()}.pdf"
    merged_local_path = f"/tmp/merged_{uuid.uuid4()}.pdf"
    
    minio_repo.download_file(file_path_1, temp_1)
    minio_repo.download_file(file_path_2, temp_2)
    
    merger = PdfMerger()
    merger.append(temp_1)
    merger.append(temp_2)
    merger.write(merged_local_path)
    merger.close()
    
    file_path_name_1 = file_path_1.split("/")[-1].split(".")[0]
    fila_path_name_2 = file_path_2.split("/")[-1].split(".")[0]
    merged_remote_name = f"files/{file_path_name_1}_{fila_path_name_2}.pdf"
    
    minio_repo.upload_file(merged_local_path, merged_remote_name)
    
    os.remove(temp_1)
    os.remove(temp_2)
    os.remove(merged_local_path)
    
    return {"status": "ok", "merged_file": merged_remote_name}

@router.get("")
async def get_files(token: str = Header(alias="auth")) -> dict[str, str]:
    user = await introspect(token=token)
    return {"call": "get_files"}

class FilesPostInput(BaseModel):
    author: str
    title: str

@router.post("")
async def post_files(token: str = Header(alias="auth"), input: FilesPostInput = Body()) -> int:
    user = await introspect(token=token)
    global id_counter
    current_id = id_counter
    id_counter += 1
    file = FileBusinesObject(
        id=current_id,
        user=user,
        title=input.title,
        author=input.author,
        path=None,
    )
    files_database[id_counter] = file
    return id_counter

@router.get("/{id}")
async def get_files_id(id: int, token: str = Header(alias="auth")) -> FileBusinesObject:
    user = await introspect(token=token)
    file = check_file_ownership(id, user)
    return files_database[id]

@router.post("/{id}")
async def post_files_id_upload(id: int, token: str = Header(alias="auth"), file_content: UploadFile = File(), minio_repo: MinioRepository = Depends(get_minio_repository)) -> dict[str, str]:
    user = await introspect(token=token)
    file = check_file_ownership(id, user)
    
    filename = str(uuid.uuid4()) + ".pdf"
    temp_path = f"/tmp/{filename}"
    remote_path = f"files/{filename}"
    
    with open(temp_path, "wb") as buffer:
        while chunk := await file_content.read(8192):
            buffer.write(chunk)
            
    minio_repo.upload_file(temp_path, remote_path)
    
    os.remove(temp_path)
    
    file.path = remote_path
    return {"status": "uploaded"}

@router.delete("/{id}")
async def delete_files_id(id: int, token: str = Header(alias="auth"), minio_repo: MinioRepository = Depends(get_minio_repository)) -> dict[str, str]:
    user = await introspect(token=token)
    file = check_file_ownership(id, user)
    
    if file.path:
        minio_repo.delete_file(file.path)
        
    del(files_database[id])
    return {"status": "deleted"}