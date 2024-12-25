from pygame import Surface, draw, gfxdraw,mixer
from pymunk import Body, Circle
from game.events.delegate import Delegate
from game.events.globalEvents import GlobalEvents
from game.gameObject import GameObject, GameObjectData
from online.onlineManager import OnlineManager
from utils.easingFunc import easeLinear


class FragmentBombEffectData(GameObjectData):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


EFFECT_TIME_MS = 500


class FragmentBombEffect(GameObject):

    def __init__(self, key: str, data: FragmentBombEffectData):
        super().__init__(key, data)

        self.body = Body(body_type=Body.KINEMATIC)
        self.body.position = (data.x, data.y)
        self.body.moment = float("inf")
        self.shapes = [Circle(self.body, 100)]
        self.shapes[0].sensor = True

        self.__effectRad : int = 0

        effectSound = mixer.Sound("assets/bomb.mp3")
        effectSound.set_volume(0.2)
        effectSound.play()

    def render(self, screen: Surface):
        if self.isExist:
            gfxdraw.filled_circle(
                screen, round(self.body.position[0]), round(self.body.position[1]), self.__effectRad, (210, 100, 10)
            )
            

    def update(self, delta: float):
        from ..tank import Tank

        self.__effectRad = round(easeLinear(delta * 1000, self.__effectRad, 500, EFFECT_TIME_MS))
        if self.__effectRad >= 300:
            GlobalEvents.GameObjectRemoving(self.key)
        if not( OnlineManager.isConnected() and OnlineManager.isClient()):
            if self.CurrentSpace is not None:
                objs= self.CurrentSpace.getGameObjectsByPosition(self.body.position,self.__effectRad)
                for obj in objs:
                    if isinstance(obj,Tank):
                        GlobalEvents.GameObjectRemoving(obj.key)

    def getData(self) -> GameObjectData:
        return FragmentBombEffectData(self.body.position[0], self.body.position[1])

    def setData(self, data: GameObjectData):
        assert isinstance(data, FragmentBombEffectData)
        self.body.position = (data.x, data.y)
