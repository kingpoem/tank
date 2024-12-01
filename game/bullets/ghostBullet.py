import numpy as np
from pygame import Surface, draw, transform
from pymunk import Body, Poly, Vec2d
from game.bullets.bullet import BULLET_COLLISION_TYPE, Bullet
from game.eventManager import EventManager
from game.resources import BACKGROUND


class GhostBullet(Bullet):
    def __init__(self, initX: float, initY: float, initAngle: float):
        def _vec_func(body: Body, gravity: tuple[float, float], damping: float, dt: float):
            # body.velocity = body.rotation_vector * 300
            body.velocity = body.velocity * 1.02
            body.update_velocity(body, (0, 0), 1, dt)
            pass

        self.body = Body(body_type=Body.KINEMATIC)
        self.body.position = (initX, initY)
        self.body.angle = initAngle
        self.body.moment = 100
        self.body.velocity = self.body.rotation_vector * 300
        self.body.velocity_func = _vec_func

        self.shapes = [Poly.create_box(self.body, (20, 4))]

        self.surface = Surface((20, 4))
        self.surface.fill((255, 255, 255))
        self.surface.set_colorkey((255, 255, 255))
        draw.polygon(
            self.surface,
            (218, 98, 125),
            [
                (0, 0),
                (self.surface.get_width(), 0),
                (self.surface.get_width(), self.surface.get_height()),
                (0, self.surface.get_height()),
            ],
        )

        event = EventManager.allocateEventType()

        def __delayCollisionTypeEventHandler():
            self.shapes[0].collision_type = BULLET_COLLISION_TYPE
            EventManager.cancelTimer(event)

        EventManager.addHandler(event, lambda e: __delayCollisionTypeEventHandler())
        EventManager.setTimer(event, 100)
        self.shapes[0].elasticity = 1

    def render(self, screen: Surface):
        vec : Vec2d = self.body.velocity
        r_s = transform.rotate(self.surface, -vec.angle_degrees)
        screen.blit(r_s, r_s.get_rect(center=self.body.position))
