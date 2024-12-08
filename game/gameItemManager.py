from typing import Callable

from loguru import logger
from pygame.event import Event
from .eventManager import EventManager
from .gameItems.fragmentWeaponGameItem import FragmentWeaponGameItem
from .gameItems.remoteControlMissileGameItem import RemoteControlMissileGameItem
from .gameItems.gameItem import GAMEITEM_COLLISION_TYPE, GameItem
from .gameItems.ghostWeaponGameItem import GhostWeaponGameItem
from .gameMap import GameMap
import random

from .defines import GAME_ITEM_APPEAR_EVENT_TYPE, GENERATE_GAME_ITEM_EVENT_TYPE
from .sceneManager import SceneManager

from structs.map import MAP_PLOT_TYPE



class GameItemManager:

    GAME_ITEMS_LIST: list[type[GameItem]] = [
        GhostWeaponGameItem,
        RemoteControlMissileGameItem,
        FragmentWeaponGameItem,
    ]

    GAME_ITEM_APPEAR_TIME = 15

    __gameMap: GameMap
    __gameItems: list[GameItem]

    def __init__(self, gameMap: GameMap):
        self.__gameMap = gameMap
        self.__gameItems = []

        EventManager.addHandler(
            GAME_ITEM_APPEAR_EVENT_TYPE,
            self.__addGameItem,
        )
        EventManager.addHandler(
            GENERATE_GAME_ITEM_EVENT_TYPE, lambda e: self.__generateRandomItem()
        )

        EventManager.setTimer(
            GENERATE_GAME_ITEM_EVENT_TYPE, GameItemManager.GAME_ITEM_APPEAR_TIME * 1000, 1
        )

    def __addGameItem(self, event: Event):
        from game.scenes.gameScene import GameScene

        item: GameItem = (event.dict["itemType"])(
            event.dict["itemPos"][0], event.dict["itemPos"][1]
        )
        item.body.angle = event.dict["itemAngle"]
        item.Removed = lambda: self.__gameItems.remove(item)
        self.__gameItems.append(item)
        if isinstance((gameScene := SceneManager.getCurrentScene()), GameScene):
            gameScene.gameObjectSpace.registerObject(item)
        else:
            return
        logger.debug(f"生成道具 {type(item)}")

    def __generateRandomItem(self):
        mapX, mapY = random.randint(0, self.__gameMap.width - 1), random.randint(
            0, self.__gameMap.height - 1
        )
        x, y = self.__gameMap.getPlotPos(mapX, mapY)
        samePosFilter: Callable[[GameItem], bool] = (
            lambda it: it.body.position.x == x and it.body.position.y == y
        )
        while self.__gameMap.map[mapX, mapY] == MAP_PLOT_TYPE.MAP_BLOCK or any(
            filter(samePosFilter, self.__gameItems)
        ):
            mapX, mapY = random.randint(0, self.__gameMap.width - 1), random.randint(
                0, self.__gameMap.height - 1
            )
            x, y = self.__gameMap.getPlotPos(mapX, mapY)

        # item.Removed = lambda: self.__gameItems.remove(item)
        # self.__gameItems.append(item)
        # self.__gameObjectManager.registerObject(item)
        # logger.debug(f"生成道具 {type(item)} 在 ({mapX}, {mapY} {self.__gameMap.map[mapX,mapY]})")
        EventManager.raiseEvent(
            Event(
                GAME_ITEM_APPEAR_EVENT_TYPE,
                {
                    "itemType": random.choice(GameItemManager.GAME_ITEMS_LIST),
                    "itemPos": (x + random.uniform(-5, 5), y + random.uniform(-5, 5)),
                    "itemAngle": random.uniform(-0.5, 0.5),
                },
            ),
        )
        EventManager.setTimer(
            GENERATE_GAME_ITEM_EVENT_TYPE,
            (GameItemManager.GAME_ITEM_APPEAR_TIME + len(self.__gameItems) * 5) * 1000,
            1,
        )

    def reset(self, gameMap: GameMap):
        self.__gameMap = gameMap
        self.__gameItems = []
        EventManager.cancelTimer(GENERATE_GAME_ITEM_EVENT_TYPE)
        EventManager.setTimer(
            GENERATE_GAME_ITEM_EVENT_TYPE,
            GameItemManager.GAME_ITEM_APPEAR_TIME * 1000,
            1,
        )
