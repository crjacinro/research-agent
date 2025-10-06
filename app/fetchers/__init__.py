from abc import abstractmethod, ABC

from app.models.results import FetcherResult

TOP_K_RESULTS = 5
MAX_CHARACTERS = 5000

class Fetcher(ABC):
    @abstractmethod
    def search(self, query: str, terms:str="") -> FetcherResult:
        pass