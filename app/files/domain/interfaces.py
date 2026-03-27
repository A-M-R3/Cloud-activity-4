from abc import ABC, abstractmethod

class FileStorageInterface(ABC):
    @abstractmethod
    async def put_file(self, local_path: str, remote_identifier: str):
        pass

    @abstractmethod
    async def get_file(self, remote_path: str, local_folder: str):
        pass

    @abstractmethod
    async def remove_file(self, remote_identifier: str):
        pass