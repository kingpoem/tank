

from typing import Any, Sequence


# class CheckData:
#     from_ : int
#     isCheck : bool
#     def __init__(self,from_ : int):
#         self.from_ = from_
#         self.isCheck = False

class EventData:
    eventType : int
    data : dict[str,Any] | None = None

    def __init__(self,eventType : int,data : dict[str,Any] | None = None):
        self.eventType = eventType
        self.data = data

class OnlineData:
    ...
