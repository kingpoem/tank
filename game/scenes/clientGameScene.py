from typing import Any
from loguru import logger
from pygame import KEYDOWN, KEYUP, Rect, Surface, key
from pygame.event import Event
from pymunk import Vec2d
from game.eventManager import EventManager
from game.gameMap import GameMap
from game.keyPressedManager import LOCAL, ONLINE
from game.operateable import Operation
from game.scenes.gameScene import GameScene
from game.scenes.localGameScene import LocalGameScene
from game.tank import TANK_STYLE, Tank
from game.weapons.weaponFactory import WEAPON_TYPE, WeaponFactory
from online.onlineManager import OnlineManager
from game.defines import GAME_ITEM_APPEAR_EVENT_TYPE, GENERATE_GAME_ITEM_EVENT_TYPE, ONLINE_KEYUP_EVENT_TYPE, ONLINE_KEYDOWN_EVENT_TYPE
from structs.map import Map

class ClientGameScene(LocalGameScene):

    __mapData : Map
    __redTankData : tuple[Vec2d,float,Operation]
    __greenTankData : tuple[Vec2d,float,Operation]

    def __init__(self,serverData : dict[str,Any]):
        logger.debug("客户端场景启动")
        self.__mapData = serverData["map"]
        self.__redTankData = serverData["redTank"]
        self.__greenTankData = serverData["greenTank"]
        super().__init__()
        EventManager.cancelTimer(GENERATE_GAME_ITEM_EVENT_TYPE)
        

    def generateMap(self):
        # 地图初始化
        gameMap = GameMap(self.__mapData)
        if self.gameObjectSpace is not None:
            self.gameObjectSpace.spaceRegion = Rect(
                0, 0, gameMap.surface.get_width(), gameMap.surface.get_height()
            )
        return gameMap
    
    def generateTanks(self):
        redTank ,greenTank = super().generateTanks()

        redTank.body.position = self.__redTankData[0]
        redTank.body.angle = self.__redTankData[1]
        redTank.operation = self.__redTankData[2]
        redTank.operation.type = ONLINE

        greenTank.body.position = self.__greenTankData[0]
        greenTank.body.angle = self.__greenTankData[1]
        greenTank.operation = self.__greenTankData[2]
        greenTank.operation.type = LOCAL

        return (redTank,greenTank)

    def process(self, event: Event):
        super().process(event)
        if event.type == KEYDOWN:
            OnlineManager.sendEvent(ONLINE_KEYDOWN_EVENT_TYPE, {"key": event.key})
        elif event.type == KEYUP:
            OnlineManager.sendEvent(ONLINE_KEYUP_EVENT_TYPE, {"key": event.key})

    def isGameMenuPauseGame(self) -> bool:
        return False
    
    def update(self, delta: float):
        # 更新画面
        self.updateGameMap(delta)
        self.updateScoreBoard(delta)
        self.updateGameMenu(delta)

    def onLeaved(self): 
        super().onLeaved()
        OnlineManager.close()

