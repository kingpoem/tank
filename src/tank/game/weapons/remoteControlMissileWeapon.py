from loguru import logger

from tank.game.bullets.missile import Missile, MissileData
from tank.game.events.eventManager import EventManager
from tank.game.events.globalEvents import GlobalEvents
from tank.game.gameObject import GameObject
from tank.game.operateable import Operateable
from tank.game.weapons.weapon import Weapon

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
    __missileKey: str | None = None

    def fire(self):
        from tank.game.operateable import Operateable
        from tank.game.tank import Tank

        if isinstance(self.owner, Operateable):

            BULLET_SHOOT_DIS = self.owner.surface.get_width() / 2 + 6

            self.__isShooted = True
            self.__missileKey = f"{self.owner.key}_Missile_{id(self)}"

            style = (255, 255, 255)
            if isinstance(self.owner, Tank):
                style = self.owner.color

            GlobalEvents.GameObjectAdding(
                self.__missileKey,
                MissileData(
                    self.owner.body.position[0]
                    + self.owner.body.rotation_vector.x * BULLET_SHOOT_DIS,
                    self.owner.body.position[1]
                    + self.owner.body.rotation_vector.y * BULLET_SHOOT_DIS,
                    self.owner.body.angle,
                    style,
                ),
            )

    def __onGameObjectAdded(self, obj: GameObject):
        if isinstance(obj, Missile) and isinstance(self.owner, Operateable):
            # 如果事件接收者与发射者不是同一个，就不接收事件
            if obj.key != self.__missileKey:
                return
            GlobalEvents.GameObjectAdded -= self.__onGameObjectAdded

            def __onBulletRemoved(obj: GameObject):
                assert isinstance(self.owner, Operateable)
                assert isinstance(obj, Missile)
                self.owner.operation = obj.operation

            obj.Removed += __onBulletRemoved
            self.__missile = obj
            self.__missile.operation = self.owner.operation
            self.owner.operation = None
            logger.debug(f"坦克发射子弹 {self} {self.__missile}")

    def canFire(self) -> bool:
        return not self.__isShooted
        # return True

    def canUse(self) -> bool:
        from tank.game.operateable import Operateable

        return not self.__isShooted and isinstance(self.owner, Operateable)

    def onPicked(self):
        GlobalEvents.GameObjectAdded += self.__onGameObjectAdded
        ...
