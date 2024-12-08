from loguru import logger
from pygame import USEREVENT
from pygame.event import Event, post
from typing import Callable


class EventManager:

    class __Timer:
        event: int | Event
        __initTimeMs : float
        timeMs: float
        loops: int
        isEndless : bool

        def __init__(self, event: int | Event, timeMs: float, loops: int = 0):
            self.event = event
            self.__initTimeMs = timeMs
            self.timeMs = timeMs
            self.loops = loops
            self.isEndless = self.loops == 0
        
        def reset(self):
            self.timeMs = self.__initTimeMs

    # class __EventHandler:
    #     eventType: int
    #     handlers: list[Callable[[Event], None]]
    #     def __init__(self, eventType: int, handlers: list[Callable[[Event], None]]):
    #         self.eventType = eventType
    #         self.handlers = handlers

    __nextEventType: int = USEREVENT + 1
    __isTimerPaused: bool = False
    __timers: list[__Timer] = []
    __eventHandlers: dict[int, list[Callable[[Event], None]]] = {}

    @staticmethod
    def isTimerPaused():
        return EventManager.__isTimerPaused

    def __init__(self):
        raise NotADirectoryError("EventManager静态类无法实例化")

    @staticmethod
    def addHandler(eventType: int, handler: Callable[[Event], None]):
        if eventType not in EventManager.__eventHandlers:
            EventManager.__eventHandlers[eventType] = []
        EventManager.__eventHandlers[eventType].append(handler)

    @staticmethod
    @logger.catch
    def removeHandler(eventType: int, handler: Callable[[Event], None] | None = None):
        if eventType not in EventManager.__eventHandlers:
            return
        if handler is None:
            EventManager.__eventHandlers.pop(eventType)
            return
        if handler in EventManager.__eventHandlers[eventType]:
            EventManager.__eventHandlers[eventType].remove(handler)

    @staticmethod
    def updateTimer(delta: float):
        if EventManager.__isTimerPaused:
            return
        for timer in EventManager.__timers:
            timer.timeMs -= delta * 1000

        acTimer = [
            t for t in EventManager.__timers if t.timeMs <= 0
        ]
        for timer in acTimer:
            logger.debug(f"定时器触发{timer.event} ")
            if isinstance(timer.event, int):
                EventManager.raiseEventType(timer.event)
            elif isinstance(timer.event, Event):
                EventManager.raiseEvent(timer.event)

            if timer.isEndless:
                timer.reset()
                continue
            timer.loops -= 1
            if timer.loops <= 0:
                EventManager.__timers.remove(timer)

    @staticmethod
    def setTimer(event: int | Event, millis: int, loops: int = 0):
        # set_timer(eventType, millis, loops)
        EventManager.__timers.append(EventManager.__Timer(event, millis, loops))
        logger.debug(f"设置定时器{event}，间隔{millis}毫秒，循环{loops}次")

    @staticmethod
    def cancelTimer(event: int | Event):
        for i in range(len(EventManager.__timers)):
            if EventManager.__timers[i].event == event:
                EventManager.__timers.pop(i)
                break

    @staticmethod
    def pauseTimer():
        EventManager.__isTimerPaused = True
        logger.debug("暂停定时器")

    @staticmethod
    def resumeTimer():
        EventManager.__isTimerPaused = False
        logger.debug("恢复定时器")

    @staticmethod
    def raiseEventType(eventType: int):
        EventManager.raiseEvent(Event(eventType))
        logger.debug(f"触发事件 {eventType}")

    @staticmethod
    def raiseEvent(event: Event):
        post(event)

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
