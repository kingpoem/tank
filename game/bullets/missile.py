from enum import Enum

import math
from loguru import logger
from pymunk import Body, Poly
from game.bullets.bullet import BULLET_COLLISION_TYPE, Bullet
from game.eventManager import EventManager
from pygame import Surface, draw, transform, image

from game.gameSettings import GlobalSettingsManager
from game.operateable import Operateable
from game.sceneManager import SceneManager


class MISSILE_TYPE(Enum):
    RED = "assets/red_missile.png"
    GREEN = "assets/green_missile.png"


class Missile(Bullet, Operateable):

    MISSILE_WIDTH = 24

    def __init__(self, initX: float, initY: float, initAngle: float, missileType: MISSILE_TYPE):
        def _vec_func(body: Body, gravity: tuple[float, float], damping: float, dt: float):
            body.velocity = (
                body.rotation_vector * GlobalSettingsManager.getGameSettings().missileSpeed
            )
            # body.velocity = body.velocity * 1.02
            body.update_velocity(body, (0, 0), 1, dt)

        o_img = image.load(missileType.value).convert_alpha()
        self.surface = transform.smoothscale_by(o_img, Missile.MISSILE_WIDTH / o_img.get_width())

        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (initX, initY)
        self.body.angle = initAngle
        self.body.moment = float("inf")
        self.body.mass = 1
        self.body.velocity = (
            self.body.rotation_vector * GlobalSettingsManager.getGameSettings().missileSpeed
        )
        self.body.velocity_func = _vec_func

        self.shapes = [
            Poly.create_box(self.body, (self.surface.get_width(), self.surface.get_height()))
        ]

        event = EventManager.allocateEventType()

        def __delayCollisionTypeEventHandler():
            self.shapes[0].collision_type = BULLET_COLLISION_TYPE
            EventManager.cancelTimer(event)

        EventManager.addHandler(event, lambda e: __delayCollisionTypeEventHandler())
        EventManager.setTimer(event, 300)

    def render(self, screen: Surface):
        # r = np.rad2deg(math.atan2(self.body.velocity[0], self.body.velocity[1])) - 90
        # print(r)
        r_img = transform.rotate(self.surface, math.degrees(-self.body.angle))
        screen.blit(r_img, r_img.get_rect(center=self.body.position))

    def onForward(self, delta: float):
        self.body.apply_force_at_world_point(
            self.body.rotation_vector * 300000 * delta, self.body.position
        )

    def onLeft(self, delta: float):
        self.body.angular_velocity = -150 * delta

    def onRight(self, delta: float):
        self.body.angular_velocity = 150 * delta

    def onShoot(self, delta: float, isFirstShoot: bool):
        if isFirstShoot and (gameObjectManager := SceneManager.getCurrentScene().gameObjectManager) is not None:
            gameObjectManager.removeObject(self)
            logger.debug(f"导弹主动销毁 {self}")
