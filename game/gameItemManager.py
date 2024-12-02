from typing import Callable

from loguru import logger
from game.eventManager import EventManager
from game.gameItems.remoteControlMissileGameItem import RemoteControlMissileGameItem
from game.gameItems.gameItem import GAMEITEM_COLLISION_TYPE, GameItem
from game.gameItems.ghostWeaponGameItem import GhostWeaponGameItem
from game.gameMap import GameMap
import random

from game.gameObjectManager import GameObjectManager

from structs.map import MAP_PLOT_TYPE


FLOAT = float


class GameItemManager:

    GAME_ITEMS_LIST: list[type[GameItem]] = [GhostWeaponGameItem, RemoteControlMissileGameItem]

    GAME_ITEM_APPEAR_EVENT_TYPE = EventManager.allocateEventType()
    GAME_ITEM_APPEAR_TIME = 15

    __gameMap: GameMap
    __gameObjectManager: GameObjectManager
    __gameItems: list[GameItem]

    def __init__(self, gameMap: GameMap, gameObjectManager: GameObjectManager):
        self.__gameMap = gameMap
        self.__gameItems = []
        self.__gameObjectManager = gameObjectManager

        EventManager.addHandler(
            GameItemManager.GAME_ITEM_APPEAR_EVENT_TYPE, lambda e: self.__generateRandomItem()
        )
        EventManager.setTimer(
            GameItemManager.GAME_ITEM_APPEAR_EVENT_TYPE,
            GameItemManager.GAME_ITEM_APPEAR_TIME * 1000,
            1,
        )

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

        item = random.choice(GameItemManager.GAME_ITEMS_LIST)(x, y)
        # 添加一点随机位置角度偏移
        item.body.angle += random.uniform(-0.5, 0.5)
        item.body.position += (random.uniform(-5, 5), random.uniform(-5, 5))

        item.Removed = lambda: self.__gameItems.remove(item)
        self.__gameItems.append(item)
        self.__gameObjectManager.registerObject(item)
        logger.debug(f"生成道具 {type(item)} 在 ({mapX}, {mapY} {self.__gameMap.map[mapX,mapY]})")
        EventManager.setTimer(
            GameItemManager.GAME_ITEM_APPEAR_EVENT_TYPE,
            (GameItemManager.GAME_ITEM_APPEAR_TIME + len(self.__gameItems) * 5) * 1000,
            1,
        )

    def reset(self, gameMap: GameMap, gameObjectManager: GameObjectManager):
        self.__gameMap = gameMap
        self.__gameObjectManager = gameObjectManager
        self.__gameItems = []
        EventManager.cancelTimer(GameItemManager.GAME_ITEM_APPEAR_EVENT_TYPE)
        EventManager.setTimer(
            GameItemManager.GAME_ITEM_APPEAR_EVENT_TYPE,
            GameItemManager.GAME_ITEM_APPEAR_TIME * 1000,
            1,
        )
