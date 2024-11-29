

from abc import ABC, abstractmethod
from pygame import Surface
from pygame.event import Event

from game.gameObjectManager import GameObjectManager

class Scene(ABC):

    @property
    @abstractmethod
    def uiSize(self) -> tuple[float,float]:
        pass

    @property
    @abstractmethod
    def gameObjectManager(self) -> GameObjectManager:
        pass

    @abstractmethod
    def process(self,event : Event):
        """
        处理事件
        """
        pass
    @abstractmethod
    def update(self, delta: float):
        """
        更新物体
        """
        pass
    @abstractmethod
    def render(self, screen: Surface):
        """
        渲染画面
        """
        pass
