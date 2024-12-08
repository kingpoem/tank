from enum import Enum
import math
from pygame.event import Event


LOCAL = 0
ONLINE = 1

class KeyPressedManager:

    __keyPressed: list[set[int]] = [set(),set()]

    def __init__(self):
        raise NotImplementedError("KeyPressedManager类不允许实例化")

    @staticmethod
    def processKeyPressed(event: Event):
        from pygame import KEYDOWN, KEYUP
        from game.defines import ONLINE_KEYDOWN_EVENT_TYPE, ONLINE_KEYUP_EVENT_TYPE

        if event.type == KEYDOWN:
            KeyPressedManager.__keyPressed[0].add(event.key)
        elif event.type == KEYUP:
            KeyPressedManager.__keyPressed[0].discard(event.key)

        if event.type == ONLINE_KEYDOWN_EVENT_TYPE:
            KeyPressedManager.__keyPressed[1].add(event.key)
        elif event.type == ONLINE_KEYUP_EVENT_TYPE:
            KeyPressedManager.__keyPressed[1].discard(event.key)

    @staticmethod
    def isPressed(key: int,type : int = LOCAL):
        return key in KeyPressedManager.__keyPressed[type]
