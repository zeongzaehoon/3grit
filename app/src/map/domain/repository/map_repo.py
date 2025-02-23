from abc import ABCMeta, abstractmethod

from map.domain.store import Store

class IMapRepository(metaclass=ABCMeta):
    
    @abstractmethod
    async def register(self, store: Store):
        raise NotImplementedError

    # @abstractmethod
    # async def find_by_id(self, id: str) -> Store:
    #     raise NotImplementedError
    
    # @abstractmethod
    # async def update(self, store: Store):
    #     raise NotImplementedError
    
    # @abstractmethod
    # async def delete(self, id: int):
    #     raise NotImplementedError