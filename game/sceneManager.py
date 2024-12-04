from enum import Enum

from game.scenes.scene import Scene


class SCENE_TYPE(Enum):
    START_SCENE = 0
    GAME_SCENE = 1


class SceneManager:

    __sceneList: dict[SCENE_TYPE, Scene]
    __currentSceneType: SCENE_TYPE

    def __init__(self):
        raise NotImplementedError("SceneManager不允许被实例化")

    @staticmethod
    def init():
        SceneManager.__currentSceneType = SCENE_TYPE.START_SCENE
        SceneManager.__sceneList = {
            SceneManager.__currentSceneType: SceneManager.__sceneTypeToScene(
                SceneManager.__currentSceneType
            )
        }

    @staticmethod
    def getCurrentScene():
        return SceneManager.__sceneList[SceneManager.__currentSceneType]

    @staticmethod
    def changeScene(sceneType: SCENE_TYPE,delOtherScene : bool = True):
        SceneManager.__currentSceneType = sceneType
        if sceneType not in SceneManager.__sceneList:
            SceneManager.__sceneList[sceneType] = SceneManager.__sceneTypeToScene(sceneType)
            SceneManager.getCurrentScene().onEntered()
        if delOtherScene:
            other_scene = [cs for cs in SceneManager.__sceneList if not cs == sceneType]
            for scene in other_scene:
                SceneManager.__sceneList[scene].onLeaved()
                SceneManager.__sceneList.pop(scene)


    @staticmethod
    def __sceneTypeToScene(sceneType: SCENE_TYPE):
        from game.scenes.startScene import StartScene
        from game.scenes.gameScene import GameScene

        SCENE_LIST: list[type[Scene]] = [StartScene, GameScene]
        return SCENE_LIST[sceneType.value]()
