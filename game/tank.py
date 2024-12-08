from enum import Enum
import math
from typing import Any
from loguru import logger
from pygame import Surface, image, transform, draw, gfxdraw
from pymunk import Arbiter, Body, CollisionHandler, Shape, Space, Poly

from game.bullets.commonBullet import CommonBullet, BULLET_COLLISION_TYPE
from game.eventManager import EventManager
from game.gameObject import GameObject
from game.gameSettings import GlobalSettingsManager
from game.operateable import Operateable, Operation
from game.sceneManager import SceneManager

from game.shootable import Shootable
from game.weapons.weapon import Weapon
from game.weapons.weaponFactory import WEAPON_TYPE, WeaponFactory
from pygame.event import Event

# TANK_HEIGHT = 60

TANK_COLLISION_TYPE = 1
TANK_REMOVED_EVENT_TYPE = EventManager.allocateEventType()


class TANK_STYLE(Enum):
    RED = "red"
    GREEN = "green"


class Tank(GameObject, Shootable, Operateable):
    """
    坦克类
    """

    TANK_WIDTH = 50

    TANK_MOVE_SPEED = 700000
    ROTATE_SPEED = 16

    __collisionHandler: CollisionHandler | None = None

    __weapon: Weapon
    __style: TANK_STYLE

    @property
    def weapon(self):
        return self.__weapon

    @weapon.setter
    def weapon(self, weapon: Weapon):
        self.__weapon = weapon
        self.refreshTankStyle()

    @property
    def style(self):
        return self.__style

    def __init__(
        self,
        initX: float,
        initY: float,
        style: TANK_STYLE,
        operation: Operation,
        weapon: Weapon | None = None,
    ):
        Operateable.__init__(self, operation)

        self.__style = style

        if weapon is None:
            self.weapon = WeaponFactory.createWeapon(self, WEAPON_TYPE.COMMON_WEAPON)
        else:
            self.weapon = weapon

        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (initX, initY)
        self.body.moment = 1000000
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
        r_img = transform.rotate(self.surface, math.degrees(-self.body.angle))
        screen.blit(r_img, r_img.get_rect(center=self.body.position))
        if self.weapon.canUse():
            self.weapon.render(screen)

    def setBody(self, space: Space):
        super().setBody(space)
        self.__collisionHandler = space.add_collision_handler(
            TANK_COLLISION_TYPE, BULLET_COLLISION_TYPE
        )
        self.__collisionHandler.post_solve = Tank.__onBulletCollision

    def shoot(self):
        # 当特殊武器不能被使用时，切换到普通武器
        if self.weapon.canUse() is False:
            self.weapon = WeaponFactory.createWeapon(self, WEAPON_TYPE.COMMON_WEAPON)

        if self.weapon.canFire():
            self.weapon.fire()

        self.refreshTankStyle()

        logger.debug(f"坦克射击 {self} {self.__weapon}")

    def refreshTankStyle(self):
        # from game.weapons.commonWeapon import CommonWeapon
        from game.weapons.ghostWeapon import GhostWeapon
        from game.weapons.remoteControlMissileWeapon import RemoteControlMissileWeapon

        lookPath = f"assets/{self.style.value}_tank.png"
        if self.weapon.canUse():
            if isinstance(self.weapon, RemoteControlMissileWeapon):
                lookPath = f"assets/{self.style.value}_tank_with_missile.png"
        # elif isinstance(weapon)

        img = image.load(lookPath).convert_alpha()
        self.surface = transform.smoothscale_by(img, Tank.TANK_WIDTH / img.get_width())

    @staticmethod
    def __onBulletCollision(arbiter: Arbiter, space: Space, data: dict[Any, Any]):
        from game.scenes.gameScene import GameScene

        if isinstance((gameScene := SceneManager.getCurrentScene()), GameScene):
            tank = gameScene.gameObjectSpace.getGameObjectByBody(arbiter.shapes[0].body)
            bullet = gameScene.gameObjectSpace.getGameObjectByBody(arbiter.shapes[1].body)
            if bullet is not None:
                gameScene.gameObjectSpace.removeObject(bullet)
            if tank is not None:
                gameScene.gameObjectSpace.removeObject(tank)
            logger.debug(f"坦克被子弹击中 {tank} {bullet}")

    def onForward(self, delta: float):
        tankSpeed = GlobalSettingsManager.getGameSettings().tankSpeed
        # 力的大小要与帧间隔成反比，因为 Ft = mv
        # 而且力会在物理世界刷新后消失
        # 所以要使获得速度一致，而帧间隔缩小，力就要增大
        self.body.apply_force_at_world_point(
            self.body.rotation_vector * tankSpeed * 1000 / delta, self.body.position
        )

    def onBack(self, delta: float):
        tankSpeed = GlobalSettingsManager.getGameSettings().tankSpeed
        self.body.apply_force_at_world_point(
            self.body.rotation_vector * -tankSpeed * 1000 / delta, self.body.position
        )

    def onLeft(self, delta: float):
        self.body.angular_velocity = -Tank.ROTATE_SPEED

    def onRight(self, delta: float):
        self.body.angular_velocity = Tank.ROTATE_SPEED

    def onShoot(self, delta: float, isFirstShoot: bool):
        from game.scenes.gameScene import GameScene

        if isFirstShoot and isinstance((gameScene := SceneManager.getCurrentScene()), GameScene):
            if gameScene.gameObjectSpace.containObject(self):
                self.shoot()

    def onRemoved(self):
        EventManager.raiseEvent(Event(TANK_REMOVED_EVENT_TYPE, {"tank": self}))
        logger.debug(f"坦克被移除 {self}")
