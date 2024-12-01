from abc import ABC, abstractmethod
from pygame import Surface
from pygame.event import Event

from game.gameObjectManager import GameObjectManager


class Scene(ABC):
    
    @property
    @abstractmethod
    def ui(self) -> Surface:
        pass

    @property
    @abstractmethod
    def gameObjectManager(self) -> GameObjectManager:
        pass

    @abstractmethod
    def process(self, event: Event):
        """
        处理事件
        """
        pass

    @abstractmethod
    def update(self, delta: float):
        """
        更新场景
        """
        pass

    def render(self, screen: Surface):
        """
        额外渲染画面
        """
        pass
