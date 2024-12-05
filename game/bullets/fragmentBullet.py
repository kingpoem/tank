from random import randint
import random
from typing import Sequence
from pygame import Surface, draw, gfxdraw
from pymunk import Body, Circle, Poly
from game.bullets.commonBullet import BULLET_COLLISION_TYPE
from game.eventManager import EventManager
from game.gameObject import GameObject
from game.gameSettings import GlobalSettingsManager
from utils.randomUtil import generateUniquePoints


class FragmentBullet(GameObject):
    """
    破片弹爆炸产生随机破片
    """

    def __init__(self, initX: float, initY: float, initAngle: float):
        def __vec_func(body: Body, gravity: tuple[float, float], damping: float, dt: float):
            body.update_velocity(body, (0, 0), 0.99, dt)
            # body.velocity = body.rotation_vector * 300
            pass

        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (initX, initY)
        self.body.angle = initAngle
        self.body.moment = 100
        self.body.mass = 100

        # self.body.velocity = (0,0)
        self.body.velocity = (
            self.body.rotation_vector * 300
        )
        self.body.velocity_func = __vec_func

        # 随机破片顶点，保证破片面积不会太小或太大
        points = list(generateUniquePoints(3, (-6, 6), (-6, 6)))
        shape = Poly(self.body, [points[0], points[1], points[2]])
        while not (16 < shape.area < 32):
            points = list(generateUniquePoints(3, (-6, 6), (-6, 6)))
            shape = Poly(self.body, [points[0], points[1], points[2]])

        self.shapes = [shape]
        shape.friction = 1
        shape.elasticity = 0
        shape.collision_type = BULLET_COLLISION_TYPE

        # self.shapes[0].collision_type = BULLET_COLLISION_TYPE
        event = EventManager.allocateEventType()

        def __delayUpSpeed():
            self.body.velocity = self.body.velocity * 1.1
            # EventManager.cancelTimer(event)

        EventManager.addHandler(event, lambda e: __delayUpSpeed())
        EventManager.setTimer(event, 100,3)

    def render(self, screen: Surface):
        shape = self.shapes[0]
        if self.body.space and isinstance(shape, Poly):
            points = shape.get_vertices()
            gfxdraw.filled_polygon(
                screen,
                [(p.rotated(self.body.angle).x + self.body.position[0], p.rotated(self.body.angle).y + self.body.position[1]) for p in points],
                (0, 0, 0),
            )
