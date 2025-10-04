from abc import abstractmethod, ABC
from typing import List

TOP_K_RESULTS = 5
MAX_CHARACTERS = 5000

class Fetcher(ABC):
    @abstractmethod
    def search(self, query: str, terms:str="") -> (List[str], List[str]):
        pass