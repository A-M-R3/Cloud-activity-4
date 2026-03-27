from typing import Optional
import httpx
import uuid
from pypdf import PdfMerger
import os

from fastapi import APIRouter, Header, HTTPException, Body, File, UploadFile
from pydantic import BaseModel

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
    print(response)
    if response.status_code != 200:
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )
    return User(**response.json())


async def introspect_aiohttp(token: str) -> User:
    url = "http://localhost:8000/introspect"
    headers = {
        "accept": "application/json",
        "auth": token
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=401, detail="Unauthorized")
            data = await response.json()

    return User(**data)


# def introspect_requests(token: str) -> User:
#     url = "http://localhost:8000/introspect"
#     headers = {
#         "accept": "application/json",
#         "auth": token
#     }
#
#     response = requests.get(url, headers=headers)
#
#     if response.status_code != 200:
#         raise HTTPException(status_code=401, detail="Unauthorized")
#
#     return User(**response.json())


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
async def post_files(token: str = Header(alias="auth"), input: PostFilesMerge = Body()) -> dict[str, str]:
    user = await introspect(token=token)
    check_file_ownership(input.file_id_1, user)
    file_1 = files_database[input.file_id_1]
    check_file_ownership(input.file_id_2, user)
    file_2 = files_database[input.file_id_2]
    file_path_1 = file_1.path
    file_path_2 = file_2.path
    pdfs = [file_path_1, file_path_2]
    file_path_name_1 = file_path_1.split("/")[-1].split(".")[0]
    fila_path_name_2 = file_path_2.split("/")[-1].split(".")[0]
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)
    merged_name = f"files/{file_path_name_1}_{fila_path_name_2}.pdf"
    merger.write(merged_name)
    merger.close()
    return {
        "status": "ok"
    }


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
async def post_files_id(id: int, token: str = Header(alias="auth"), file_content: UploadFile = File()) -> dict[str, str]:
    user = await introspect(token=token)
    file = check_file_ownership(id, user)
    filename = str(uuid.uuid4())
    prefix = "files/"
    with open(prefix + filename + ".pdf", "wb") as buffer:
        while chunk := await file_content.read(8192):
            buffer.write(chunk)
    file.path = prefix + filename + ".pdf"
    return {}


@router.delete("/{id}")
async def post_files_id(id: int, token: str = Header(alias="auth")) -> dict[str, str]:
    user = await introspect(token=token)
    file = check_file_ownership(id, user)
    os.remove(files_database[id].path)
    del(files_database[id])
    return {}
