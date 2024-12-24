from enum import Enum
import math
from typing import Any
from loguru import logger
from numpy import isin
from pygame import Surface, image, transform, draw, gfxdraw,mixer
from pymunk import Arbiter, Body, CollisionHandler, Shape, Space, Poly

from game.bullets.commonBullet import CommonBullet, BULLET_COLLISION_TYPE
from game.events.eventManager import EventManager
from game.events.globalEvents import GlobalEvents
from game.gameObject import GameObject, GameObjectData
from game.gameSettings import GlobalSettingsManager
from game.operateable import Operateable, Operation
from game.sceneManager import SceneManager

from game.weapons.weapon import Weapon
from game.weapons.weaponFactory import WEAPON_TYPE, WeaponFactory
from pygame.event import Event

# TANK_HEIGHT = 60

TANK_COLLISION_TYPE = 1
TANK_REMOVED_EVENT_TYPE = EventManager.allocateEventType()


class TANK_STYLE(Enum):
    RED = "red"
    GREEN = "green"


class TankData(GameObjectData):
    def __init__(
        self,
        x: float,
        y: float,
        angle: float,
        style: TANK_STYLE,
        operation: Operation | None = None,
        weaponType: WEAPON_TYPE | None = None,
    ):
        self.x = x
        self.y = y
        self.angle = angle
        self.style = style
        self.operation = operation
        self.weaponType = weaponType


class Tank(GameObject, Operateable):
    """
    坦克类
    """

    TANK_WIDTH = 50

    TANK_MOVE_SPEED = 700000
    ROTATE_SPEED = 24

    __collisionHandler: CollisionHandler | None = None

    __weapon: Weapon | None = None
    __style: TANK_STYLE

    @property
    def weapon(self):
        if self.__weapon is None:
            w = WeaponFactory.createWeapon(self, WEAPON_TYPE.COMMON_WEAPON)
            self.weapon = w
            return w
        return self.__weapon

    @weapon.setter
    def weapon(self, weapon: Weapon):
        from .weapons.commonWeapon import CommonWeapon
        if self.__weapon is not None:
            self.__weapon.onDropped()
        self.__weapon = weapon
        if not isinstance(self.__weapon,CommonWeapon):
            self.__onEquippedSound.play()
        self.__weapon.onPicked()
        self.refreshTankStyle()

    @property
    def style(self):
        return self.__style
    
    @style.setter
    def style(self, style: TANK_STYLE):
        self.__style = style
        self.refreshTankStyle()

    def __init__(
        self,
        key: str,
        data: TankData,
    ):
        GameObject.__init__(self, key, data)
        Operateable.__init__(self, data.operation)

        # 音效
        self.__shootSound = mixer.Sound("assets/shoot.mp3")
        self.__shootSound.set_volume(0.2)

        self.__onEquippedSound = mixer.Sound("assets/tank_equipped.mp3")
        self.__onEquippedSound.set_volume(0.2)

        self.style = data.style

        if data.weaponType is None:
            self.weapon = WeaponFactory.createWeapon(self, WEAPON_TYPE.COMMON_WEAPON)
        else:
            self.weapon = WeaponFactory.createWeapon(self, data.weaponType)

        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (data.x, data.y)
        self.body.angle = data.angle
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
            self.__shootSound.play()

        self.refreshTankStyle()

        logger.debug(f"坦克射击 {self.key} {type(self.__weapon)}")

    def refreshTankStyle(self):
        # from game.weapons.commonWeapon import CommonWeapon
        from game.weapons.ghostWeapon import GhostWeapon
        from game.weapons.remoteControlMissileWeapon import RemoteControlMissileWeapon
        from game.weapons.fragmentBombWeapon import FragmentBombWeapon

        lookPath = f"assets/{self.style.value}_tank.png"
        if self.weapon.canUse():
            if isinstance(self.weapon, RemoteControlMissileWeapon):
                lookPath = f"assets/{self.style.value}_tank_with_missile.png"
            elif isinstance(self.weapon, GhostWeapon):
                lookPath = f"assets/{self.style.value}_tank_with_ghost.png"
            elif isinstance(self.weapon, FragmentBombWeapon):
                lookPath = f"assets/{self.style.value}_tank_with_bomb.png"
        # elif isinstance(weapon)

        img = image.load(lookPath).convert_alpha()
        self.surface = transform.smoothscale_by(img, Tank.TANK_WIDTH / img.get_width())

    @staticmethod
    def __onBulletCollision(arbiter: Arbiter, space: Space, data: dict[Any, Any]):
        from game.scenes.gameScene import GameScene

        if not arbiter.is_first_contact:
            return
        if isinstance((gameScene := SceneManager.getCurrentScene()), GameScene):
            tank = gameScene.gameObjectSpace.getGameObjectByBody(arbiter.shapes[0].body)
            bullet = gameScene.gameObjectSpace.getGameObjectByBody(arbiter.shapes[1].body)
            if bullet is not None:
                GlobalEvents.GameObjectRemoving(bullet.key)
            if tank is not None:
                GlobalEvents.GameObjectRemoving(tank.key)
            logger.debug(f"坦克被子弹击中 {tank} {bullet}")

    def onForward(self, delta: float):
        tankSpeed = GlobalSettingsManager.getGameSettings().tankSpeed
        # 力的大小要与帧间隔成反比，因为 Ft = mv
        # 而且力会在物理世界刷新后消失
        # 所以要使获得速度一致，而帧间隔缩小，力就要增大
        self.body.apply_force_at_world_point(
            self.body.rotation_vector * tankSpeed * 5000 / delta, self.body.position
        )

    def onBack(self, delta: float):
        tankSpeed = GlobalSettingsManager.getGameSettings().tankSpeed
        self.body.apply_force_at_world_point(
            self.body.rotation_vector * -tankSpeed * 5000 / delta, self.body.position
        )

    def onLeft(self, delta: float):
        self.body.angular_velocity = -Tank.ROTATE_SPEED

    def onRight(self, delta: float):
        self.body.angular_velocity = Tank.ROTATE_SPEED

    def onShoot(self, delta: float, isFirstShoot: bool):
        from game.scenes.gameScene import GameScene

        if isFirstShoot and isinstance((gameScene := SceneManager.getCurrentScene()), GameScene):
            if self.isExist:
                self.shoot()

    def getData(self) -> GameObjectData:
        return TankData(
            self.body.position[0],
            self.body.position[1],
            self.body.angle,
            self.style,
            self.operation,
            WeaponFactory.getWeaponType(self.weapon),
        )

    def setData(self, data: GameObjectData):
        assert isinstance(data, TankData)
        self.body.position = (data.x, data.y)
        self.body.angle = data.angle
        self.style = data.style
        self.operation = data.operation
        if data.weaponType is not None:
            self.weapon = WeaponFactory.createWeapon(self, data.weaponType)
            