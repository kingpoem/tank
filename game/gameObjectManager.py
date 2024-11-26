from pygame import Surface
from pymunk import Body
from game.gameObject import GameObject
from game.gameSpace import GameSpace


class GameObjectManager:

    __objects: set[GameObject] = set()

    # 阻止实例化
    def __init__(self):
        raise NotImplementedError("GameObjectManager是静态类不允许实例化")

    @staticmethod
    def registerObject(object: GameObject):
        if object in GameObjectManager.__objects:
            return
        GameObjectManager.__objects.add(object)
        object.setBody(GameSpace.getSpace())

    @staticmethod
    def removeObject(object: GameObject):
        GameObjectManager.__objects.remove(object)
        object.removeBody(GameSpace.getSpace())
        if object.Removed is not None:
            object.Removed()

    @staticmethod
    def drawObjects(screen: Surface):
        for obj in GameObjectManager.__objects:
            obj.draw(screen)

    @staticmethod
    def getGameObjectByBody(body: Body):
        for obj in GameObjectManager.__objects:
            if obj.body == body:
                return obj
        return None

    @staticmethod
    def containObject(object: GameObject):
        return object in GameObjectManager.__objects
