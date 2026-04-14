from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel
from any2json_py.utils.cost_tracker import CostTracker


class BaseParser(ABC):
    @abstractmethod
    def parse(self, path: Path, model: type[BaseModel], tracker: CostTracker) -> BaseModel:
        ...
