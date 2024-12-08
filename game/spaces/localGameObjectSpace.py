

from loguru import logger
from pygame import Rect, Surface
from pymunk import Body, Space
from game.gameObject import GameObject
from game.spaces.gameObjectSpace import GameObjectSpace


class LocalGameObjectSpace(GameObjectSpace):
    __objects: list[GameObject]
    __space : Space
    __spaceRegion: Rect | None = None
    """
    空间范围
    超过这个范围的物体会被移除世界
    """

    @property
    def objects(self):
        return tuple(self.__objects)
    
    @property
    def space(self):
        return self.__space

    @property
    def spaceRegion(self):
        return self.__spaceRegion
    @spaceRegion.setter
    def spaceRegion(self, value: Rect | None):
        self.__spaceRegion = value

    def __init__(self):
        self.__objects = list()
        self.__space = Space()
        self.__space.damping = 0

    def registerObject(self, object: GameObject):
        if object in self.__objects:
            return
        self.__objects.append(object)
        object.setBody(self.space)
        object.onEntered()

    def removeObject(self, object: GameObject):

        if object not in self.__objects:
            return
        self.__objects.remove(object)
        object.removeBody(self.space)
        object.onRemoved()
        if object.Removed is not None:
            object.Removed()

    def clearObjects(self):
        for obj in self.__objects:
            obj.removeBody(self.space)
            obj.onRemoved()
            if obj.Removed is not None:
                obj.Removed()
        self.__objects.clear()

    def updateObjects(self, delta: float):
        from game.operateable import Operateable
        
        for obj in self.objects:
            if isinstance(obj, Operateable):
                obj.operate(delta)
        DETAIL_NUM = 8
        for i in range(DETAIL_NUM):
            self.__space.step(delta / DETAIL_NUM)
        if self.__spaceRegion is not None:
            for obj in self.__objects:
                if not self.__spaceRegion.collidepoint(obj.body.position):
                    self.removeObject(obj)
                    logger.debug(f"游戏物体 {obj} 超出世界范围")

    def renderObjects(self, screen: Surface):
        for obj in self.__objects:
            obj.render(screen)

    def getGameObjectByBody(self, body: Body):
        for obj in self.__objects:
            if obj.body == body:
                return obj
        return None

    def containObject(self, object: GameObject):
        return object in self.__objects