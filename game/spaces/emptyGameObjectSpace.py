

from pymunk import Space
from game.gameObject import GameObject
from game.spaces.gameObjectSpace import GameObjectSpace




class EmptyGameObjectSpace(GameObjectSpace):

    __emptySpace : Space = Space()

    @property
    def objects(self):
        return ()
    
    @property
    def space(self):
        return self.__emptySpace
    
    @property
    def spaceRegion(self):
        return None
    
    @spaceRegion.setter
    def spaceRegion(self, value):
        ...

    def registerObject(self, object: GameObject):
        ...

    def removeObject(self, object: GameObject):
        ...

    def clearObjects(self):
        ...

    def updateObjects(self, delta: float):
        ...

    def renderObjects(self, screen):
        ...

    def getGameObjectByBody(self, body) -> GameObject | None:
        return None
    
    def containObject(self, object: GameObject) -> bool:
        return False