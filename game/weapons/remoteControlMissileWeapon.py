from loguru import logger
from game.bullets.commonBullet import CommonBullet
from game.bullets.missile import MISSILE_TYPE, Missile
from game.eventManager import EventManager
from game.gameObject import GameObject

from game.sceneManager import SceneManager
from game.scenes.gameScene import GameScene
from game.weapons.weapon import Weapon


class RemoteControlMissileWeapon(Weapon):
    """
    遥控导弹武器
    发射遥控导弹
    导弹发出后玩家将控制导弹而不是坦克
    再次发射将取消导弹
    """

    __MISSILE_DISAPPEAR_EVENT_TYPE: int

    __isShooted: bool = False

    __missile: Missile | None = None

    def __init__(self, owner: GameObject):
        super().__init__(owner)
        self.__MISSILE_DISAPPEAR_EVENT_TYPE = EventManager.allocateEventType()

    def fire(self):
        from game.tank import Tank, TANK_STYLE
        from game.operateable import Operateable

        if isinstance(self.owner, Operateable):

            BULLET_DISAPPEAR_TIME_MS = 8 * 1000
            BULLET_SHOOT_DIS = self.owner.surface.get_width() / 2 - 4

            self.__isShooted = True

            self.__missile = Missile(
                self.owner.body.position[0] + self.owner.body.rotation_vector.x * BULLET_SHOOT_DIS,
                self.owner.body.position[1] + self.owner.body.rotation_vector.y * BULLET_SHOOT_DIS,
                self.owner.body.angle,
                (
                    MISSILE_TYPE.RED
                    if isinstance(self.owner, Tank) and self.owner.style is TANK_STYLE.RED
                    else MISSILE_TYPE.GREEN
                ),
            )

            # 超过指定时间子弹自动消失
            def __bulletOutOfTimeDisappear() -> None:
                if isinstance(gameScene := SceneManager.getCurrentScene(),GameScene):
                    if self.__missile is not None and gameScene.gameObjectSpace.containObject(
                        self.__missile
                    ):
                        gameScene.gameObjectSpace.removeObject(self.__missile)
                        logger.debug(f"导弹超时消失 {self.__missile}")
                EventManager.cancelTimer(self.__MISSILE_DISAPPEAR_EVENT_TYPE)

            o = self.owner.operation

            def __onBulletDisappear():
                if isinstance(self.owner, Operateable):
                    self.owner.operation = o
                EventManager.cancelTimer(self.__MISSILE_DISAPPEAR_EVENT_TYPE)
                

            if o is not None:
                self.owner.operation = None
                self.__missile.operation = o
                self.__missile.Removed = __onBulletDisappear
                if isinstance(gameScene := SceneManager.getCurrentScene(),GameScene):
                    gameScene.gameObjectSpace.registerObject(self.__missile)
                EventManager.addHandler(
                    self.__MISSILE_DISAPPEAR_EVENT_TYPE, lambda e: __bulletOutOfTimeDisappear()
                )
                EventManager.setTimer(self.__MISSILE_DISAPPEAR_EVENT_TYPE, 30 * 1000)
                logger.debug(f"坦克发射子弹 {self} {self.__missile}")

    def canFire(self) -> bool:
        return not self.__isShooted
        # return True

    def canUse(self) -> bool:
        from game.operateable import Operateable

        return not self.__isShooted and isinstance(self.owner, Operateable)
