import math
from random import randint
import random
from loguru import logger
from pygame import K_DOWN, K_ESCAPE, KEYDOWN, QUIT, Rect, Surface
import pygame
from pygame.event import Event
from pygame.freetype import Font
from pymunk import Space

# from game.gameLoop import GameLoop
from game.controls.floatMenu import FloatMenu
from game.controls.selectionControl import Selection, SelectionControl
from game.operateable import Operateable, Operation
from game.sceneManager import SCENE_TYPE, SceneManager
from game.scenes.gameScene import GameScene
from game.spaces.gameObjectSpace import GAMEOBJECT_SPACE_TYPE, GameObjectSpace
from game.weapons.commonWeapon import CommonWeapon
from game.eventManager import EventManager
from game.gameItems.gameItem import GameItem
from game.gameItemManager import GameItemManager
from game.gameMap import (
    MAP_MAX_HEIGHT,
    MAP_MAX_WIDTH,
    MAP_MIN_HEIGHT,
    MAP_MIN_WIDTH,
    MARGIN_X,
    MARGIN_Y,
    PLOT_HEIGHT,
    PLOT_WIDTH,
    GameMap,
)
from game.tank import TANK_STYLE, Tank
from game.weapons.weaponFactory import WEAPON_TYPE, WeaponFactory
from structs.map import Map


SCORE_UI_HEIGHT = 192
GAME_OVER_EVENT_TYPE: int = EventManager.allocateEventType()


class LocalGameScene(GameScene):

    def __init__(self):
        logger.debug("本地游戏场景初始化")
        super().__init__(GameObjectSpace.create(GAMEOBJECT_SPACE_TYPE.LOCAL))

    def generateMap(self):
        # 地图初始化
        width = randint(MAP_MIN_WIDTH // 2, MAP_MAX_WIDTH // 2) * 2 + 1
        height = randint(MAP_MIN_HEIGHT // 2, MAP_MAX_HEIGHT // 2) * 2 + 1
        gameMap = GameMap(Map(width, height))
        if self.gameObjectSpace is not None:
            self.gameObjectSpace.spaceRegion = Rect(
                0, 0, gameMap.surface.get_width(), gameMap.surface.get_height()
            )
        return gameMap

    def generateTanks(self):
        # 坦克初始化
        pos = self.gameMap.getPlotPos(1, 1)
        redTank = Tank(
            pos[0],
            pos[1],
            TANK_STYLE.RED,
            Operation(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g),
        )
        pos = self.gameMap.getPlotPos(self.gameMap.width - 2, self.gameMap.height - 2)
        greenTank = Tank(
            pos[0],
            pos[1],
            TANK_STYLE.GREEN,
            Operation(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_KP_0),
        )
        # # 添加一点随机位置角度偏移
        redTank.body.angle = random.uniform(0, math.pi)
        redTank.body.position += (random.uniform(-5, 5), random.uniform(-5, 5))

        greenTank.body.angle = random.uniform(0, math.pi)
        greenTank.body.position += (random.uniform(-5, 5), random.uniform(-5, 5))

        redTank.weapon = WeaponFactory.createWeapon(redTank, WEAPON_TYPE.FRAGMENTBOMB_WEAPON)
        greenTank.weapon = WeaponFactory.createWeapon(greenTank, WEAPON_TYPE.COMMON_WEAPON)

        return (redTank, greenTank)

    def startNewTurn(self):
        self.gameObjectSpace.clearObjects()
        self.gameMap = self.generateMap()
        self.redTank, self.greenTank = self.generateTanks()
        self.gameItemManager.reset(self.gameMap)

        # 决定渲染顺序
        self.gameObjectSpace.registerObject(self.gameMap)
        self.gameObjectSpace.registerObject(self.redTank)
        self.gameObjectSpace.registerObject(self.greenTank)
        return True