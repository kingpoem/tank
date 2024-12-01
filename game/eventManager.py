from loguru import logger
from pygame import USEREVENT
import pygame
from pygame.event import Event, post
from pygame.time import set_timer
from typing import Callable


class EventManager:

    __nextEventType: int = USEREVENT + 1
    __eventHandlers: dict[int, list[Callable[[Event], None]]] = {}

    def __init__(self):
        raise NotADirectoryError("EventManager静态类无法实例化")

    @staticmethod
    def addHandler(eventType: int, handler: Callable[[Event], None]):
        if eventType not in EventManager.__eventHandlers:
            EventManager.__eventHandlers[eventType] = []
        EventManager.__eventHandlers[eventType].append(handler)

    @staticmethod
    @logger.catch
    def removeHandler(eventType: int, handler: Callable[[Event], None]):
        EventManager.__eventHandlers[eventType].remove(handler)

    @staticmethod
    def setTimer(eventType: int, millis: int, loops: int = 0):
        set_timer(eventType, millis, loops)
        logger.debug(f"设置定时器{eventType}，间隔{millis}毫秒，循环{loops}次")

    @staticmethod
    def cancelTimer(eventType: int):
        set_timer(eventType, 0, 0)

    @staticmethod
    def raiseEvent(eventType: int):
        post(Event(eventType))

    @staticmethod
    def handleEvent(event: Event):
        tasks: list[Callable[[Event], None]] = []
        if event.type in EventManager.__eventHandlers:
            for handler in EventManager.__eventHandlers[event.type]:
                tasks.append(handler)
        for task in tasks:
            try:
                task(event)
            except Exception:
                logger.exception("事件处理器出错，已跳过")

    @staticmethod
    def allocateEventType():
        eventType = EventManager.__nextEventType
        EventManager.__nextEventType += 1
        return eventType
