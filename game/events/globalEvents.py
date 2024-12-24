from abc import ABC
from typing import Callable, final

from .eventDelegate import EventDelegate
from ..gameObject import GameObject, GameObjectData


@final
class GlobalEvents(ABC):

    GameObjectAdding = EventDelegate[str, GameObjectData]("游戏对象被尝试添加", True)
    GameObjectAdded = EventDelegate[GameObject]("游戏对象被添加")
    GameObjectRemoving = EventDelegate[str]("游戏对象被尝试移除",True)
    GameObjectRemoved = EventDelegate[str]("游戏对象被移除")
    GameObjectsClearing = EventDelegate[None]("所有游戏对象被尝试清空", True)

    GameScoreUpdated = EventDelegate[int, int]("游戏分数被更新", True)