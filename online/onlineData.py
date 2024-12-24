from abc import ABC
from typing import Any, Sequence

from game.gameObject import GameObjectData


class OnlineData(ABC): ...


# class CheckData:
#     from_ : int
#     isCheck : bool
#     def __init__(self,from_ : int):
#         self.from_ = from_
#         self.isCheck = False


class EventData(OnlineData):
    eventType: int
    data: dict[str, Any] | None = None

    def __init__(self, eventType: int, data: dict[str, Any] | None = None):
        self.eventType = eventType
        self.data = data


class GameUpdateData(OnlineData):
    def __init__(self, data: dict[str, GameObjectData]):
        self.data = data

