from enum import Enum
from typing import Any
from loguru import logger
import numpy as np
from pygame import Surface, image, transform, draw, gfxdraw
from pymunk import Arbiter, Body, CollisionHandler, Shape, Space, Poly

from game.bullets.bullet import Bullet, BULLET_COLLISION_TYPE
from game.eventManager import EventManager
from game.gameObject import GameObject
from game.gameObjectManager import GameObjectManager
from game.sceneManager import SceneManager
from game.weapons.weapon import Weapon
from game.weapons.weaponFactory import WEAPON_TYPE, WeaponFactory

# TANK_HEIGHT = 60

TANK_COLLISION_TYPE = 1


class TANK_STYLE(Enum):
    RED = "assets/red_tank.png"
    GREEN = "assets/green_tank.png"


class Tank(GameObject):
    """
    坦克类
    """

    TANK_WIDTH = 50

    __collisionHandler: CollisionHandler | None = None

    __gameObjectManager: GameObjectManager

    @property
    def gameObjectManager(self):
        return self.__gameObjectManager

    __weapon: Weapon | None

    @property
    def weapon(self):
        return self.__weapon

    @weapon.setter
    def weapon(self, weapon: Weapon):
        self.__weapon = weapon

    def __init__(
        self,
        initX: float,
        initY: float,
        style: TANK_STYLE,
        gameObjectManager: GameObjectManager,
        weapon: Weapon | None = None,
    ):
        self.__gameObjectManager = gameObjectManager

        self.__weapon = weapon

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
            shape.collision_type = TANK_COLLISION_TYPE
            shape.friction = 1

        pass

    def render(self, screen: Surface):
        # 旋转图片 pymunk和pygame旋转方向相反
        if self.body.space:

            r_img = transform.rotate(self.surface, np.rad2deg(-self.body.angle))
            screen.blit(r_img, r_img.get_rect(center=self.body.position))

    def setBody(self, space: Space):
        super().setBody(space)
        self.__collisionHandler = space.add_collision_handler(
            TANK_COLLISION_TYPE, BULLET_COLLISION_TYPE
        )
        self.__collisionHandler.post_solve = Tank.__onBulletCollision

    def shoot(self):
        if self.__weapon is not None:
            # 当特殊武器不能被使用时，切换到普通武器
            if self.__weapon.canUse() is False:
                commonWeapon = WeaponFactory.createWeapon(self, WEAPON_TYPE.COMMON_WEAPON)
                if isinstance(self.__weapon, type(commonWeapon)) is False:
                    self.__weapon = commonWeapon

            if self.__weapon.canFire():
                self.__weapon.fire()
        logger.debug(f"坦克射击 {self} {self.__weapon}")

    @staticmethod
    def __onBulletCollision(arbiter: Arbiter, space: Space, data: dict[Any, Any]):
        # self.removeBody(Space)
        tank = SceneManager.getCurrentScene().gameObjectManager.getGameObjectByBody(arbiter.shapes[0].body)
        bullet = SceneManager.getCurrentScene().gameObjectManager.getGameObjectByBody(arbiter.shapes[1].body)
        if bullet is not None:
            SceneManager.getCurrentScene().gameObjectManager.removeObject(bullet)
        if tank is not None:
            SceneManager.getCurrentScene().gameObjectManager.removeObject(tank)
        logger.debug(f"坦克被子弹击中 {tank} {bullet}")
