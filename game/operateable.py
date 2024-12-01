from abc import ABC
from typing import final


from pygame.event import Event
from game.eventManager import EventManager


class Operation:

    forwardKey: int
    """前进按键"""
    backKey: int
    """后退按键"""
    leftKey: int
    """左转按键"""
    rightKey: int
    """右转按键"""
    shootKey: int
    """射击按键"""

    def __init__(self, forwardKey: int, backKey: int, leftKey: int, rightKey: int, shootKey: int):
        self.forwardKey = forwardKey
        self.backKey = backKey
        self.leftKey = leftKey
        self.rightKey = rightKey
        self.shootKey = shootKey
        pass


class Operateable(ABC):

    __operation: Operation | None = None

    @property
    def operation(self):
        return self.__operation

    @operation.setter
    def operation(self, value: Operation | None):
        from pygame import KEYDOWN

        self.__operation = value
        if (value is not None and value.shootKey is None) or value is None:
            EventManager.removeHandler(KEYDOWN, self.__onShootKeyDownHandler)
        else:
            EventManager.addHandler(KEYDOWN, self.__onShootKeyDownHandler)

    def __init__(self, operation: Operation | None):
        from pygame import KEYDOWN
        

        self.__operation = operation
        EventManager.addHandler(KEYDOWN, self.__onShootKeyDownHandler)

    def __onShootKeyDownHandler(self,e: Event):
        if self.operation is not None and e.key == self.operation.shootKey:
            self.onShoot()

    @final
    def operate(self, delta: float):
        from pygame import key

        if self.operation is None:
            return
        pressed = key.get_pressed()
        if pressed[self.operation.forwardKey]:
            self.onForward(delta)
        if pressed[self.operation.backKey]:
            self.onBack(delta)
        if pressed[self.operation.leftKey]:
            self.onLeft(delta)
        if pressed[self.operation.rightKey]:
            self.onRight(delta)

    def onForward(self, delta: float):
        pass

    def onBack(self, delta: float):
        pass

    def onLeft(self, delta: float):
        pass

    def onRight(self, delta: float):
        pass

    def onShoot(self):
        pass
