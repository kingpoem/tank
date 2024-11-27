from threading import Timer
from typing import Tuple
from pygame import Surface, draw
from pygame.event import Event
from pymunk import Body, Circle, Shape, Space

from game.eventManager import EventManager
from game.gameObject import GameObject
from game.gameSpace import GameSpace


BULLET_COLLISION_TYPE = 2


class Bullet(GameObject):

    def __init__(self, initX: float, initY: float, initAngle: float):
        def _vec_func(body: Body, gravity: Tuple[float, float], damping: float, dt: float):
            # body.velocity = body.rotation_vector * 300
            body.update_velocity(body, (0, 0), 1, dt)
            pass

        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (initX, initY)
        self.body.angle = initAngle
        self.body.moment = 100
        self.body.mass = 1

        # self.body.velocity = (0,0)
        self.body.velocity = self.body.rotation_vector * 300
        self.body.velocity_func = _vec_func

        self.shapes = [Circle(self.body, 4)]

        # self.shapes[0].collision_type = BULLET_COLLISION_TYPE
        event = EventManager.allocateEventType()

        def __delayCollisionTypeEventHandler():
            self.shapes[0].collision_type = BULLET_COLLISION_TYPE
            EventManager.cancelTimer(event)

        # TimerManager.registerTimer(Timer(0.1, __delayCollisionType))
        EventManager.addHandler(event, lambda e: __delayCollisionTypeEventHandler())
        EventManager.setTimer(event, 100)
        self.shapes[0].elasticity = 1

        pass

    def render(self, screen: Surface):
        if self.body.space:
            draw.circle(screen, (0, 0, 0), self.body.position, 4)
        pass
