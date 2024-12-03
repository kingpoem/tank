from abc import abstractmethod

from pygame import Surface
from game.contracts.renderable import Renderable
from pygame.event import Event


class Control(Renderable):

    @property
    @abstractmethod
    def ui(self) -> Surface: ...

    @abstractmethod
    def process(self, event: Event): ...

    @abstractmethod
    def update(self, delta: float): ...
