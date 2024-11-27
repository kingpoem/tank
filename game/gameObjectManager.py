from pygame import Surface
from pymunk import Body
from game.gameObject import GameObject
from game.gameSpace import GameSpace


class GameObjectManager:

    __objects: list[GameObject]

    def __init__(self):
        self.__objects = list()

    def registerObject(self, object: GameObject):
        if object in self.__objects:
            return
        self.__objects.append(object)
        object.setBody(GameSpace.getSpace())

    def removeObject(self, object: GameObject):
        if object not in self.__objects:
            return
        self.__objects.remove(object)
        object.removeBody(GameSpace.getSpace())
        if object.Removed is not None:
            object.Removed()

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
