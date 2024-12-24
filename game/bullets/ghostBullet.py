import math
from selectors import SelectorKey
import numpy as np
from pygame import Surface, draw, transform
from pymunk import Body, Poly, Vec2d
from game.bullets.commonBullet import BULLET_COLLISION_TYPE, CommonBullet
from game.events.eventDelegate import EventDelegate
from game.events.eventManager import EventManager
from game.events.globalEvents import GlobalEvents
from game.gameObject import GameObject, GameObjectData
from game.defines import BACKGROUND
from game.gameSettings import GlobalSettingsManager

class GhostBulletData(GameObjectData):
    def __init__(self,x : float,y : float,angle : float):
        self.x = x
        self.y = y
        self.angle = angle

class GhostBullet(GameObject):
    """
    幽灵子弹
    """
    BULLET_DISAPPEAR_TIME_MS = 5_000

    BulletDisappeared: EventDelegate[GameObject]

    def __init__(self,key:str, data : GhostBulletData):
        super().__init__(key, data)

        self.BulletDisappeared = EventDelegate[GameObject](f"{key} 幽灵子弹 消失")
        self.BulletDisappeared.setTimer(GhostBullet.BULLET_DISAPPEAR_TIME_MS, 1, self)
        self.BulletDisappeared += lambda obj : GlobalEvents.GameObjectRemoving(obj.key)

        def __vec_func(body: Body, gravity: tuple[float, float], damping: float, dt: float):
            # body.velocity = body.rotation_vector * 300
            body.velocity = body.velocity * (1 + GlobalSettingsManager.getGameSettings().ghostSpeedIncreaseRate)
            body.update_velocity(body, (0, 0), 1, dt)
            

        self.body = Body(body_type=Body.KINEMATIC)
        self.body.position = (data.x, data.y)
        self.body.angle = data.angle
        # self.body.moment = float('inf')
        self.body.velocity = self.body.rotation_vector * GlobalSettingsManager.getGameSettings().ghostBulletSpeed
        self.body.velocity_func = __vec_func

        self.shapes = [Poly.create_box(self.body, (20, 4))]
        self.shapes[0].elasticity = 1

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

        # event = EventManager.allocateEventType()
        tempEvent = EventDelegate[None](f"{key} 幽灵子弹 延迟设置碰撞")

        def __delayCollisionTypeEventHandler(_ : None):
            self.shapes[0].collision_type = BULLET_COLLISION_TYPE
            
        tempEvent += __delayCollisionTypeEventHandler
        tempEvent.setTimer(100, 1, None)


    def render(self, screen: Surface):
        r_s = transform.rotate(self.surface, math.degrees(-self.body.angle))
        screen.blit(r_s, r_s.get_rect(center=self.body.position))

    def getData(self) -> GameObjectData:
        return GhostBulletData(self.body.position[0], self.body.position[1], self.body.angle)
    
    def setData(self, data: GameObjectData):
        assert isinstance(data, GhostBulletData)
        self.body.position = (data.x, data.y)
        self.body.angle = data.angle