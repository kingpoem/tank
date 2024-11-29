

from enum import Enum
from game.scenes.scene import Scene

class SCENE_TYPE(Enum):
    GAME_SCENE = 0

class SceneManager:

    __sceneList : list[Scene]
    __currentSceneType: SCENE_TYPE



    def __init__(self):
        raise NotImplementedError("SceneManager不允许被实例化")
    
    @staticmethod
    def init():
        from game.scenes.gameScene import GameScene
        SceneManager.__sceneList = [GameScene()]
        SceneManager.__currentSceneType = SCENE_TYPE.GAME_SCENE

    @staticmethod
    def getCurrentScene():
        return SceneManager.__sceneList[SceneManager.__currentSceneType.value]
    
    @staticmethod
    def changeScene(sceneType : SCENE_TYPE):
        SceneManager.__currentSceneType = sceneType
