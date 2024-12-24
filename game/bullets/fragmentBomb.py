from pygame import Surface, draw
from pymunk import Body, Circle, Shape
from game.bullets.commonBullet import BULLET_COLLISION_TYPE, CommonBullet
from game.events.eventDelegate import EventDelegate
from game.events.eventManager import EventManager
from game.events.globalEvents import GlobalEvents
from game.gameObject import GameObject, GameObjectData
from game.gameSettings import GlobalSettingsManager


class FragmentBombData(GameObjectData):
    def __init__(self,x : float,y : float,angle : float):
        self.x = x
        self.y = y
        self.angle = angle


class FragmentBomb(GameObject):
    """
    破片炮弹
    """
    BULLET_DISAPPEAR_TIME_MS = 8_000

    BulletDisappeared: EventDelegate[GameObject]

    def __init__(self,key : str, data : FragmentBombData):
        super().__init__(key, data)

        self.BulletDisappeared = EventDelegate[GameObject](f"{key} 破片炮弹 消失")
        self.BulletDisappeared.setTimer(FragmentBomb.BULLET_DISAPPEAR_TIME_MS, 1, self)
        self.BulletDisappeared += lambda obj : GlobalEvents.GameObjectRemoving(obj.key)

        def __vec_func(body: Body, gravity: tuple[float, float], damping: float, dt: float):
            body.update_velocity(body, (0, 0), 1, dt)
            # body.velocity = body.rotation_vector * 300
            pass

        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (data.x, data.y)
        self.body.angle = data.angle
        self.body.moment = float('inf')
        self.body.mass = 1

        # self.body.velocity = (0,0)
        self.body.velocity = (
            self.body.rotation_vector * GlobalSettingsManager.getGameSettings().commonBulletSpeed
        )
        self.body.velocity_func = __vec_func

        self.shapes = [Circle(self.body, 6)]
        # 设置子弹摩擦力为0
        self.shapes[0].friction = 0
        # 设置弹性系数为 1，完全反弹
        self.shapes[0].elasticity = 1
        # self.shapes[0].sensor = True
        # self.shapes[0].collision_type = BULLET_COLLISION_TYPE
        tempEvent = EventDelegate[None](f"{key} 破片炮弹 延迟设置碰撞")

        def __delayEnableCollisionEventHandler(_ : None):
            # self.shapes[0].sensor = False
            self.shapes[0].collision_type = BULLET_COLLISION_TYPE

        tempEvent += __delayEnableCollisionEventHandler
        tempEvent.setTimer(100, 1, None)


    def render(self, screen: Surface):
        if self.body.space:
            draw.circle(screen, (0, 0, 0), self.body.position, 8)

    def getData(self) -> GameObjectData:
        return FragmentBombData(self.body.position[0], self.body.position[1], self.body.angle)
    
    def setData(self, data: GameObjectData):
        assert isinstance(data, FragmentBombData)
        self.body.position = (data.x, data.y)
        self.body.angle = data.angle