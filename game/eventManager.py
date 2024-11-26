from loguru import logger
from pygame import USEREVENT
from pygame.event import Event
from pygame.time import set_timer
from typing import Callable


class EventManager:

    __nextEventId: int = USEREVENT + 1
    __eventHandlers: dict[int, list[Callable[[Event], None]]] = {}

    def __init__(self):
        raise NotADirectoryError("EventManager静态类无法实例化")

    @staticmethod
    def addHandler(eventId: int, handler: Callable[[Event], None]):
        if eventId not in EventManager.__eventHandlers:
            EventManager.__eventHandlers[eventId] = []
        EventManager.__eventHandlers[eventId].append(handler)

    @staticmethod
    @logger.catch
    def removeHandler(eventId: int, handler: Callable[[Event], None]):
        EventManager.__eventHandlers[eventId].remove(handler)

    @staticmethod
    def setTimer(eventId: int, millis: int, loops: int = 0):
        set_timer(eventId, millis, loops)

    @staticmethod
    def cancelTimer(eventId: int):
        set_timer(eventId, 0, 0)

    @staticmethod
    def handleEvent(event: Event):
        if event.type in EventManager.__eventHandlers:
            for handler in EventManager.__eventHandlers[event.type]:
                try:
                    handler(event)
                except Exception:
                    logger.exception("事件处理器出错，已跳过")

    @staticmethod
    def allocateEventId():
        eventId = EventManager.__nextEventId
        EventManager.__nextEventId += 1
        return eventId
    
    # @staticmethod
    # def allocateEventIdBy(obj : object):
    #     eventId = EventManager.__nextEventId + id(obj)
    #     EventManager.__nextEventId = eventId + 1
    #     return eventId