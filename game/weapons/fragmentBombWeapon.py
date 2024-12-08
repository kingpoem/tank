import math
from typing import Sequence
from loguru import logger
from pygame import Surface
from pymunk import Body, Shape
from game.bullets.fragmentBomb import FragmentBomb
from game.bullets.fragmentBullet import FragmentBullet
from game.eventManager import EventManager
from game.gameObject import GameObject
from game.sceneManager import SceneManager
from game.scenes.gameScene import GameScene
from game.weapons.weapon import Weapon


class FragmentBombWeapon(Weapon):
    """
    破片炮弹武器
    发生破片炮弹
    """

    __isShooted: bool = False

    def fire(self):
        BULLET_DISAPPEAR_TIME_MS = 8 * 1000
        BULLET_SHOOT_DIS = self.owner.surface.get_width() / 2 + 6

        self.__isShooted = True

        event = EventManager.allocateEventType()
        bullet = FragmentBomb(
            self.owner.body.position[0] + self.owner.body.rotation_vector[0] * BULLET_SHOOT_DIS,
            self.owner.body.position[1] + self.owner.body.rotation_vector[1] * BULLET_SHOOT_DIS,
            self.owner.body.angle,
        )

        # 超过指定时间子弹自动消失
        def __bulletOutOfTimeDisappear(bullet: GameObject, e: int) -> None:
            if isinstance(gameScene := SceneManager.getCurrentScene(),GameScene):
                if gameScene.gameObjectSpace.containObject(bullet):
                    gameScene.gameObjectSpace.removeObject(bullet)
                    logger.debug(f"子弹超时消失 {bullet}")
                EventManager.cancelTimer(e)

        def __onBulletDisappear():
            # 随机生成向四面八方的破片
            FRAG_NUM = 32
            angles = [(i / FRAG_NUM) * math.pi for i in range(FRAG_NUM)]
            frags: list[FragmentBullet] = []
            for i, angle in enumerate(angles):
                frags.append(
                    FragmentBullet(
                        bullet.body.position[0] + math.cos(angle) * 4,
                        bullet.body.position[1] + math.sin(angle) * 4,
                        angle,
                    )
                )
                if isinstance(gameScene := SceneManager.getCurrentScene(),GameScene):
                    gameScene.gameObjectSpace.registerObject(frags[i])

            eventf = EventManager.allocateEventType()

            def __onFragBulletDisappear(frags: Sequence[FragmentBullet]):
                if isinstance(gameScene := SceneManager.getCurrentScene(),GameScene):
                    for frag in frags:
                        gameScene.gameObjectSpace.removeObject(frag)
                    logger.debug(f"破片超时消失")

            EventManager.addHandler(eventf, lambda e: __onFragBulletDisappear(frags))
            EventManager.setTimer(eventf, 2000, 1)

        bullet.Removed = __onBulletDisappear
        if isinstance(gameScene := SceneManager.getCurrentScene(),GameScene):
            gameScene.gameObjectSpace.registerObject(bullet)
        EventManager.addHandler(event, lambda e: __bulletOutOfTimeDisappear(bullet, event))
        EventManager.setTimer(event, BULLET_DISAPPEAR_TIME_MS, 1)

        logger.debug(f"坦克发射子弹 {self} {bullet}")

    def canFire(self) -> bool:
        return not self.__isShooted

    def canUse(self) -> bool:
        return not self.__isShooted

