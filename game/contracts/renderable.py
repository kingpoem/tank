from abc import ABC, abstractmethod
from pygame import Surface


class Renderable(ABC):
    @abstractmethod
    def render(self, screen: Surface): ...
