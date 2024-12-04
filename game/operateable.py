from abc import ABC
from typing import final


from pygame.event import Event
from game.eventManager import EventManager
from game.sceneManager import SceneManager


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
    __isFirstShoot: bool = False

    @property
    def operation(self):
        return self.__operation

    @operation.setter
    def operation(self, value: Operation | None):
        # from pygame import KEYDOWN

        self.__operation = value

    def __init__(self, operation: Operation | None):
        # from pygame import KEYDOWN
        self.__operation = operation

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

        if pressed[self.operation.shootKey]:
            self.onShoot(delta, self.__isFirstShoot)
            self.__isFirstShoot = False
        else:
            self.__isFirstShoot = True

    def onForward(self, delta: float):
        """
        当处于前进状态时
        """
        pass

    def onBack(self, delta: float):
        """
        当处于后退状态时
        """
        pass

    def onLeft(self, delta: float):
        """
        当处于左转状态时
        """
        pass

    def onRight(self, delta: float):
        """
        当处于右转状态时
        """
        pass

    def onShoot(self, delta: float, isFirstShoot: bool):
        pass
