from loguru import logger
from pygame import KEYDOWN, key
from pygame.event import Event
from game.eventManager import EventManager
from game.tank import Tank


class PlayerOperation:

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

    # def isForward(self) -> bool:
    #     return key.get_pressed()[self.forwardKey]

    # def isBack(self) -> bool:
    #     return key.get_pressed()[self.backKey]

    # def isLeft(self) -> bool:
    #     return key.get_pressed()[self.leftKey]

    # def isRight(self) -> bool:
    #     return key.get_pressed()[self.rightKey]


class Player:
    tank: Tank
    operation: PlayerOperation

    def __init__(self, tank: Tank, operation: PlayerOperation):
        def __onShootKeyDownHandler(e: Event):
            if e.key == operation.shootKey:
                tank.shoot()
                

        self.tank = tank
        self.operation = operation
        EventManager.addHandler(KEYDOWN, __onShootKeyDownHandler)
        pass

    def move(self, delta: float):
        pressed = key.get_pressed()
        # dSpeed = 0
        dAngle = 0
        dPower = 0
        # b.velocity = b.velocity * 0.9
        # b.angular_velocity = b.angular_velocity * 0.9
        if pressed[self.operation.leftKey]:
            dAngle -= 100
        if pressed[self.operation.rightKey]:
            dAngle += 100
        self.tank.body.angular_velocity = dAngle * delta
        if pressed[self.operation.forwardKey]:
            dPower += 300000
        if pressed[self.operation.backKey]:
            dPower -= 300000

        if dPower != 0:
            self.tank.body.apply_force_at_world_point(
                self.tank.body.rotation_vector * dPower * delta * self.tank.body.mass,
                self.tank.body.position,
            )
        pass
