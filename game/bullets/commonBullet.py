
from pygame import Surface, draw
from pygame.event import Event
from pymunk import Body, Circle, Shape, Space

from game.eventManager import EventManager
from game.gameObject import GameObject
from game.gameSettings import GlobalSettingsManager


BULLET_COLLISION_TYPE = 2


class CommonBullet(GameObject):
    """
    常规子弹
    """

    def __init__(self, initX: float, initY: float, initAngle: float):
        def __vec_func(body: Body, gravity: tuple[float, float], damping: float, dt: float):
            body.update_velocity(body, (0, 0), 1, dt)
            # body.velocity = body.rotation_vector * 300
            pass

        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (initX, initY)
        self.body.angle = initAngle
        self.body.moment = float('inf')
        self.body.mass = 1

        # self.body.velocity = (0,0)
        self.body.velocity = self.body.rotation_vector * GlobalSettingsManager.getGameSettings().commonBulletSpeed
        self.body.velocity_func = __vec_func

        self.shapes = [Circle(self.body, 4)]
        # 设置子弹摩擦力为0
        self.shapes[0].friction = 0

        # self.shapes[0].collision_type = BULLET_COLLISION_TYPE
        event = EventManager.allocateEventType()

        def __delayCollisionTypeEventHandler():
            self.shapes[0].collision_type = BULLET_COLLISION_TYPE
            EventManager.cancelTimer(event)


        EventManager.addHandler(event, lambda e: __delayCollisionTypeEventHandler())
        EventManager.setTimer(event, 100)
        # 设置弹性系数为 1，完全反弹
        self.shapes[0].elasticity = 1


    def render(self, screen: Surface):
        if self.body.space:
            draw.circle(screen, (0, 0, 0), self.body.position, 4)
