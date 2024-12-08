from abc import ABC, abstractmethod
from enum import Enum
from typing import Sequence, final

from pygame import Rect
from pymunk import Space

from game.gameObject import GameObject



class GAMEOBJECT_SPACE_TYPE(Enum):
    EMPTY = 0
    LOCAL = 1
    SERVER = 2
    CLIENT = 3

class GameObjectSpace(ABC):

    @property
    @abstractmethod
    def objects(self) -> tuple[GameObject, ...]:
        """
        游戏对象列表
        """
        ...

    @property
    @abstractmethod
    def space(self) -> Space:
        """
        物理空间
        """
        ...

    @property
    @abstractmethod
    def spaceRegion(self) -> Rect | None:
        """
        空间有效区域
        """
        ...

    @spaceRegion.setter
    @abstractmethod
    def spaceRegion(self, value: Rect | None): ...

    @abstractmethod
    def registerObject(self, object: GameObject):
        """
        注册游戏对象
        """
        ...

    @abstractmethod
    def removeObject(self, object: GameObject):
        """
        移除游戏对象
        """
        ...

    @abstractmethod
    def clearObjects(self):
        """
        清除所有游戏对象
        """
        ...

    @abstractmethod
    def updateObjects(self, delta: float):
        """
        更新游戏对象
        """
        ...

    @abstractmethod
    def renderObjects(self, screen):
        """
        渲染游戏对象
        """
        ...

    @abstractmethod
    def getGameObjectByBody(self, body) -> GameObject | None:
        """
        通过游戏刚体获取对应的游戏对象
        """
        ...

    @abstractmethod
    def containObject(self, object: GameObject) -> bool:
        """
        判断游戏对象是否在游戏世界中
        """
        ...

    @final
    @staticmethod
    def create(type: GAMEOBJECT_SPACE_TYPE):
        from game.spaces.emptyGameObjectSpace import EmptyGameObjectSpace
        from game.spaces.localGameObjectSpace import LocalGameObjectSpace
        from game.spaces.serverGameObjectSpace import ServerGameObjectSpace
        from game.spaces.clientGameObjectSpace import ClientGameObjectSpace

        return [
            EmptyGameObjectSpace,
            LocalGameObjectSpace,
            ServerGameObjectSpace,
            ClientGameObjectSpace,
        ][type.value]()



    
