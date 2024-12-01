from loguru import logger
from game.bullets.bullet import Bullet
from game.bullets.ghostBullet import GhostBullet
from game.eventManager import EventManager
from game.sceneManager import SceneManager
from game.tank import Tank
from game.weapons.weapon import Weapon


class GhostWeapon(Weapon):
    """
    幽灵坦克武器
    发射幽灵子弹
    """

    TOTAL_MAX_BULLET = 10
    MAX_BULLET = 5
    __shootBulletCount: int = 0
    __totalShootBulletCount: int = 0

    def fire(self):
        BULLET_DISAPPEAR_TIME_MS = 5 * 1000
        BULLET_SHOOT_DIS = self.owner.surface.get_width() / 2 - 4

        # if self.owner.body.space:

        self.__shootBulletCount += 1
        self.__totalShootBulletCount += 1
        bullet = GhostBullet(
            self.owner.body.position[0] + self.owner.body.rotation_vector.x * BULLET_SHOOT_DIS,
            self.owner.body.position[1] + self.owner.body.rotation_vector.y * BULLET_SHOOT_DIS,
            self.owner.body.angle,
        )
        
        event = EventManager.allocateEventType()

        # 超过指定时间子弹自动消失
        def __bulletOutOfTimeDisappear(bullet: Bullet) -> None:
            if SceneManager.getCurrentScene().gameObjectManager.containObject(bullet):
                SceneManager.getCurrentScene().gameObjectManager.removeObject(bullet)
                logger.debug(f"子弹超时消失 {bullet}")
            EventManager.cancelTimer(event)

        def __onBulletDisappear():
            self.__shootBulletCount = max(0, self.__shootBulletCount - 1)
            EventManager.cancelTimer(event)

        bullet.Removed = __onBulletDisappear
        SceneManager.getCurrentScene().gameObjectManager.registerObject(bullet)
        EventManager.addHandler(event, lambda e: __bulletOutOfTimeDisappear(bullet))
        EventManager.setTimer(event, BULLET_DISAPPEAR_TIME_MS)

        logger.debug(f"坦克发射子弹 {self} {bullet}")

    def canFire(self) -> bool:
        return self.__shootBulletCount < GhostWeapon.MAX_BULLET

    def canUse(self) -> bool:
        return self.__totalShootBulletCount < GhostWeapon.TOTAL_MAX_BULLET
