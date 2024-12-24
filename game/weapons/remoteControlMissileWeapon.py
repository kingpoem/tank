from loguru import logger
from game.bullets.commonBullet import CommonBullet
from game.bullets.missile import MISSILE_TYPE, Missile, MissileData
from game.events.eventManager import EventManager
from game.events.globalEvents import GlobalEvents
from game.gameObject import GameObject, GameObjectFactory

from game.operateable import Operateable
from game.sceneManager import SceneManager
from game.scenes.gameScene import GameScene
from game.weapons.weapon import Weapon
from pygame.event import Event


MISSILE_DISAPPEAR_EVENT_TYPE = EventManager.allocateEventType()


class RemoteControlMissileWeapon(Weapon):
    """
    遥控导弹武器
    发射遥控导弹
    导弹发出后玩家将控制导弹而不是坦克
    再次发射将取消导弹
    """

    __isShooted: bool = False

    __missile: Missile | None = None

    def fire(self):
        from game.tank import Tank, TANK_STYLE
        from game.operateable import Operateable

        if isinstance(self.owner, Operateable):

            BULLET_SHOOT_DIS = self.owner.surface.get_width() / 2 - 4

            self.__isShooted = True
            key = f"{self.owner.key}_Missile_{id(self)}"

            o = self.owner.operation
            assert o is not None

            self.owner.operation = None

            GlobalEvents.GameObjectAdding(
                key,
                MissileData(
                    self.owner.body.position[0]
                    + self.owner.body.rotation_vector.x * BULLET_SHOOT_DIS,
                    self.owner.body.position[1]
                    + self.owner.body.rotation_vector.y * BULLET_SHOOT_DIS,
                    self.owner.body.angle,
                    (
                        MISSILE_TYPE.RED
                        if isinstance(self.owner, Tank) and self.owner.style is TANK_STYLE.RED
                        else MISSILE_TYPE.GREEN
                    ),
                ),
            )

    def __onGameObjectAdded(self, obj: GameObject):
        if isinstance(obj, Missile):

            def __onBulletRemoved(obj: GameObject):
                assert isinstance(self.owner, Operateable)
                assert isinstance(obj, Missile)
                self.owner.operation = obj.operation

            obj.Removed += __onBulletRemoved
            self.__missile = obj
            self.__missile.operation = obj.operation
            logger.debug(f"坦克发射子弹 {self} {self.__missile}")

    def canFire(self) -> bool:
        return not self.__isShooted
        # return True

    def canUse(self) -> bool:
        from game.operateable import Operateable

        return not self.__isShooted and isinstance(self.owner, Operateable)

    def onPicked(self):
        GlobalEvents.GameObjectAdded += self.__onGameObjectAdded
        ...

    def onDropped(self):
        GlobalEvents.GameObjectAdded -= self.__onGameObjectAdded
        ...

