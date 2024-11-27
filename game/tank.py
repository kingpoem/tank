from enum import Enum
from threading import Timer
from typing import Any
from loguru import logger
import numpy as np
from pygame import Surface, image, transform, draw, gfxdraw
from pymunk import Arbiter, Body, CollisionHandler, Shape, Space, Poly

from game.bullet import Bullet, BULLET_COLLISION_TYPE
from game.eventManager import EventManager
from game.gameObject import GameObject
from game.gameObjectManager import GameObjectManager
from game.gameSpace import GameSpace

# TANK_HEIGHT = 60


# TANK_COLLISION_TYPE = 1
class TANK_STYLE(Enum):
    RED = "assets/red_tank.png"
    GREEN = "assets/green_tank.png"
    GREY = "assets/grey_tank.png"


class Tank(GameObject):
    TANK_WIDTH = 50
    TANK_MAX_BULLET = 5

    __collisionHandler: CollisionHandler | None = None
    __shotBulletCount: int = 0
    __gameObjectManager : GameObjectManager

    def __init__(
        self, initX: float, initY: float, style: TANK_STYLE, gameObjectManager: GameObjectManager
    ):
        self.__gameObjectManager = gameObjectManager
        o_img = image.load(style.value).convert_alpha()
        self.surface = transform.smoothscale_by(
            o_img,
            Tank.TANK_WIDTH / o_img.get_width(),
        )
        # self.img.fill((255, 255, 0, 0), special_flags=pygame.BLEND_RGBA_MAX)
        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (initX, initY)
        self.body.moment = 10000
        self.body.mass = 100

        TANK_BODY_RATE = 0.6
        TANK_GUN_RATE = 0.2

        self.shapes = [
            Poly(
                self.body,
                [
                    (-self.surface.get_width() / 2, -self.surface.get_height() / 2),
                    (
                        (self.surface.get_width() / 2) * TANK_BODY_RATE,
                        -self.surface.get_height() / 2,
                    ),
                    (
                        (self.surface.get_width() / 2) * TANK_BODY_RATE,
                        self.surface.get_height() / 2,
                    ),
                    (-self.surface.get_width() / 2, self.surface.get_height() / 2),
                ],
            ),
            Poly(
                self.body,
                [
                    (
                        0,
                        (-self.surface.get_height() / 2) * TANK_GUN_RATE,
                    ),
                    (
                        (self.surface.get_width() / 2),
                        (-self.surface.get_height() / 2) * TANK_GUN_RATE,
                    ),
                    (
                        (self.surface.get_width() / 2),
                        (self.surface.get_height() / 2) * TANK_GUN_RATE,
                    ),
                    (
                        0,
                        (self.surface.get_height() / 2) * TANK_GUN_RATE,
                    ),
                ],
            ),
        ]
        for shape in self.shapes:
            shape.collision_type = id(self)
            shape.friction = 1

        pass

    def render(self, screen: Surface):
        # 旋转图片 pymunk和pygame旋转方向相反
        if self.body.space:

            r_img = transform.rotate(self.surface, np.rad2deg(-self.body.angle))
            screen.blit(r_img, r_img.get_rect(center=self.body.position))

    def setBody(self, space: Space):
        super().setBody(space)
        self.__collisionHandler = space.add_collision_handler(id(self), BULLET_COLLISION_TYPE)
        # self.__collisionHandler.pre_solve = self.__onPreSolveBulletCollision
        self.__collisionHandler.post_solve = self.__onBulletCollision

    def shoot(self):
        BULLET_DISAPPEAR_TIME_MS = 8 * 1000
        BULLET_SHOOT_DIS = self.surface.get_width() / 2 - 4

        if self.body.space:

            if self.__shotBulletCount >= Tank.TANK_MAX_BULLET:
                return
            self.__shotBulletCount += 1
            bullet = Bullet(
                self.body.position.x + self.body.rotation_vector.x * BULLET_SHOOT_DIS,
                self.body.position.y + self.body.rotation_vector.y * BULLET_SHOOT_DIS,
                self.body.angle,
            )
            event = EventManager.allocateEventType()

            # 超过指定时间子弹自动消失
            def __bulletOutOfTimeDisappear(bullet: Bullet) -> None:
                if self.__gameObjectManager.containObject(bullet):
                    self.__gameObjectManager.removeObject(bullet)
                    logger.debug(f"子弹超时消失 {bullet}")
                EventManager.cancelTimer(event)

            def __onBulletDisappear():
                self.__shotBulletCount = max(0, self.__shotBulletCount - 1)
                EventManager.cancelTimer(event)

            bullet.Removed = __onBulletDisappear
            self.__gameObjectManager.registerObject(bullet)
            EventManager.addHandler(event, lambda e: __bulletOutOfTimeDisappear(bullet))
            EventManager.setTimer(event, BULLET_DISAPPEAR_TIME_MS)

            logger.debug(f"坦克发射子弹 {self} {bullet}")

    def __onBulletCollision(self, arbiter: Arbiter, space: Space, data: dict[Any, Any]):
        # self.removeBody(Space)
        obj = self.__gameObjectManager.getGameObjectByBody(arbiter.shapes[1].body)
        if obj is not None:
            self.__gameObjectManager.removeObject(obj)
            self.__gameObjectManager.removeObject(self)
            logger.debug(f"坦克被子弹击中 {self} {obj}")
