from abc import ABC, abstractmethod
import math
from random import randint
import random
from typing import Any, Callable, Sequence
from loguru import logger
from pygame import K_DOWN, K_ESCAPE, KEYDOWN, KEYUP, QUIT, Rect, Surface
import pygame
from pygame import transform
from pygame.event import Event
from pygame.freetype import Font
from pymunk import Space

# from game.gameLoop import GameLoop
from game import tank
from game.controls.floatMenu import FloatMenu
from game.controls.selectionControl import Selection, SelectionControl
from game.defines import (
    BACKGROUND,
    FONT_COLOR,
    GENERATE_GAME_ITEM_EVENT_TYPE,
    MEDIAN_FONT,
    ONLINE_KEYDOWN_EVENT_TYPE,
    ONLINE_KEYUP_EVENT_TYPE,
    SELECTION_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from game.events.eventDelegate import EventDelegate
from game.events.globalEvents import GlobalEvents
from game.gameObject import GameObject, GameObjectData, GameObjectFactory
from game.keyPressedManager import ONLINE
from game.operateable import Operateable, Operation
from game.sceneManager import SCENE_TYPE, SceneManager
from game.spaces.gameObjectSpace import GAMEOBJECT_SPACE_TYPE, GameObjectSpace
from game.events.eventManager import EventManager
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
    GameMapData,
)
from game.scenes.scene import Scene
from game.tank import TANK_REMOVED_EVENT_TYPE, TANK_STYLE, Tank, TankData
from game.weapons.weaponFactory import WEAPON_TYPE
from online.onlineData import GameUpdateData
from online.onlineManager import OnlineManager

SCORE_UI_HEIGHT = 192

class ClientGameScene(Scene):
    
    __gameObjectSpace: GameObjectSpace
    __gameItemManager: GameItemManager | None = None

    __gameMap: GameMap

    __redScore: int = 0
    __greenScore: int = 0

    __ui: Surface
    __gameUI: Surface
    __scoreUI: Surface
    __gameMenu: FloatMenu

    __redTank: Tank
    __greenTank: Tank
    __isLoaded: bool = False
    __isScoreChanged: bool = True

    GameLoaded: EventDelegate[None]

    @property
    def ui(self):
        return self.__ui

    @property
    def gameMap(self):
        return self.__gameMap

    @gameMap.setter
    def gameMap(self, value: GameMap):
        self.__gameMap = value

    @property
    def redTank(self):
        return self.__redTank

    @redTank.setter
    def redTank(self, value: Tank):
        self.__redTank = value

    @property
    def greenTank(self):
        return self.__greenTank

    @greenTank.setter
    def greenTank(self, value: Tank):
        self.__greenTank = value

    @property
    def gameObjectSpace(self):
        return self.__gameObjectSpace

    @property
    def gameItemManager(self):
        return self.__gameItemManager

    def __init__(self):
        logger.info("游戏场景初始化")

        self.GameLoaded = EventDelegate[None]("游戏加载完毕")

        self.__gameObjectSpace = GameObjectSpace()
        self.registerEvents()

        self.__gameUI = pygame.Surface(
            (
                WINDOW_WIDTH,
                WINDOW_HEIGHT - SCORE_UI_HEIGHT,
            )
        )
        self.__scoreUI = pygame.Surface((WINDOW_WIDTH, SCORE_UI_HEIGHT))
        self.__ui = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.__gameMenu = FloatMenu(
            self.__ui,
            1080,
            480,
            SelectionControl(
                1080,
                480,
                [
                    Selection(
                        lambda: "返回主菜单",
                        SELECTION_HEIGHT,
                        lambda: SceneManager.changeScene(SCENE_TYPE.START_SCENE),
                    ),
                    Selection(
                        lambda: "退出游戏",
                        SELECTION_HEIGHT,
                        lambda: EventManager.raiseEventType(QUIT),
                    ),
                ],
            ),
        )
        OnlineManager.GameObjectChanged += self.__onGameObjectChanged

    def registerEvents(self):

        self.GameLoaded += self.__onGameLoaded
        GlobalEvents.GameObjectAdding += self.__onGameObjectAdding
        GlobalEvents.GameObjectAdded += self.__onGameObjectAdded
        GlobalEvents.GameObjectRemoving += self.__onGameObjectRemoving
        GlobalEvents.GameObjectsClearing += self.__onGameObjectClearing

        GlobalEvents.GameScoreUpdated += self.__onGameScoreUpdated
        # EventManager.addHandler(GAME_OBJECT_ADD_EVENT_TYPE,self.__onGameObjectAdded)
        # EventManager.addHandler(GAME_OBJECT_REMOVE_EVENT_TYPE,self.__onGameObjectRemoved)
        # EventManager.addHandler(GAME_OBJECT_CLEAR_EVENT_TYPE,self.__onClearGameObject)

    def unregisterEvents(self):

        self.GameLoaded.clear()
        GlobalEvents.GameObjectAdding.clear()
        GlobalEvents.GameObjectAdded.clear()
        GlobalEvents.GameObjectRemoving.clear()
        GlobalEvents.GameObjectsClearing.clear()

        GlobalEvents.GameScoreUpdated.clear()
        # EventManager.removeHandler(GAME_OBJECT_ADD_EVENT_TYPE)
        # EventManager.removeHandler(GAME_OBJECT_REMOVE_EVENT_TYPE)
        # EventManager.removeHandler(GAME_OBJECT_CLEAR_EVENT_TYPE)

    def __onGameScoreUpdated(self,redScore:int,greenScore:int):
        if redScore == self.__redScore and greenScore == self.__greenScore:
            return
        self.__redScore = redScore
        self.__greenScore = greenScore
        self.__isScoreChanged = True

    def __gameMapAdded(self):
        if self.__gameItemManager is not None:
            self.__gameItemManager.reset(self.__gameMap)
        else:
            if not (OnlineManager.isConnected() and OnlineManager.isClient()):
                self.__gameItemManager = GameItemManager(self.__gameMap, self.__gameObjectSpace)
        if self.gameObjectSpace is not None:
            self.gameObjectSpace.spaceRegion = Rect(
                0, 0, self.__gameMap.surface.get_width(), self.__gameMap.surface.get_height()
            )

    def __onGameObjectChanged(self, key: str, data: GameObjectData):
        if key in self.__gameObjectSpace.objects:
            self.__gameObjectSpace.objects[key].setData(data)

    def __onGameObjectAdding(self, key: str, data: GameObjectData):
        logger.debug(f"{key} adding")
        self.__gameObjectSpace.registerObject(GameObjectFactory.create(key, data))

    def __onGameObjectAdded(self, obj: GameObject):
        logger.debug(self.__gameObjectSpace.objects)
        if isinstance(obj, Tank):
            if obj.key == "RedTank":
                self.__redTank = obj
            elif obj.key == "GreenTank":
                self.__greenTank = obj
                self.GameLoaded(None)

        elif isinstance(obj, GameMap):
            self.__gameMap = obj
            self.__gameMapAdded()

    def __onGameObjectRemoving(self, key: str):
        logger.debug(f"{key} removing")
        if key in self.__gameObjectSpace.objects:
            self.__gameObjectSpace.removeObject(key)
            logger.debug(self.__gameObjectSpace.objects)
        else:
            logger.warning(f"对象{key}不存在 删除操作无效")

    def __onGameObjectClearing(self, _: None):
        self.__gameObjectSpace.clearObjects()

    def startNewTurn(self) -> bool:
        """
        开始新一轮游戏
        返回值False则代表开始最后一轮，之后不在重新开始
        """
        GlobalEvents.GameObjectsClearing(None)
        gameMapData = self.generateMapData()

        # 决定渲染顺序
        GlobalEvents.GameObjectAdding("GameMap", gameMapData)

        return True

    def generateMapData(self) -> GameMapData:
        # 地图初始化
        width = randint(MAP_MIN_WIDTH // 2, MAP_MAX_WIDTH // 2) * 2 + 1
        height = randint(MAP_MIN_HEIGHT // 2, MAP_MAX_HEIGHT // 2) * 2 + 1
        return GameMapData(width, height)

    def generateTankDatas(self) -> Sequence[TankData]:
        # 坦克初始化

        return (
            TankData(
                self.gameMap.getPlotPos(1, 1)[0] + random.uniform(-5, 5),
                self.gameMap.getPlotPos(1, 1)[1] + random.uniform(-5, 5),
                random.uniform(0, math.pi),
                TANK_STYLE.RED,
                Operation(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g),
                WEAPON_TYPE.COMMON_WEAPON,
            ),
            TankData(
                self.gameMap.getPlotPos(self.gameMap.width - 2, self.gameMap.height - 2)[0]
                + random.uniform(-5, 5),
                self.gameMap.getPlotPos(self.gameMap.width - 2, self.gameMap.height - 2)[1]
                + random.uniform(-5, 5),
                random.uniform(0, math.pi),
                TANK_STYLE.GREEN,
                Operation(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_KP_0),
                WEAPON_TYPE.COMMON_WEAPON,
            ),
        )

    def process(self, event: Event):
        if self.__gameMenu.isMenuShow:
            self.__gameMenu.process(event)
            if self.__gameMenu.isMenuShow is False:
                return

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if self.__gameMenu.isMenuShow is False:
                    self.__gameMenu.show()
        self.__trySendKeyEvent(event)

    def update(self, delta: float):
        # 更新画面
        self.updateGameMap(delta)
        self.__ui.blit(
            self.__gameUI,
            (0, 0),
        )
        self.updateScoreBoard(delta)
        self.__ui.blit(self.__scoreUI, (0, WINDOW_HEIGHT - self.__scoreUI.get_height()))
        self.updateGameMenu(delta)

    def updateGameMap(self, delta: float):
        if self.__isLoaded is False:
            return
        self.__gameUI.fill(BACKGROUND)
        self.__gameObjectSpace.renderObjects(self.__gameUI)

    def updateScoreBoard(self, delta: float):
        if self.__isLoaded is False or self.__isScoreChanged is False:
            return
        self.__scoreUI.fill(BACKGROUND)
        self.__scoreUI.blit(
            self.__redTank.surface,
            (
                self.__scoreUI.get_width() / 2 - 100 - self.__redTank.surface.get_width() / 2,
                PLOT_HEIGHT / 2 - self.__redTank.surface.get_height() / 2,
            ),
        )
        self.__scoreUI.blit(
            self.__greenTank.surface,
            (
                self.__scoreUI.get_width() / 2 + 100 - self.__greenTank.surface.get_width() / 2,
                PLOT_HEIGHT / 2 - self.__greenTank.surface.get_height() / 2,
            ),
        )
        scoreSurface1, scoreRect1 = MEDIAN_FONT.render(f"{self.__redScore}", FONT_COLOR)
        self.__scoreUI.blit(
            scoreSurface1,
            (
                self.__scoreUI.get_width() / 2
                - 100
                + self.__redTank.surface.get_width()
                - scoreRect1.width / 2,
                PLOT_HEIGHT / 2 - scoreRect1.height / 2,
            ),
        )
        scoreSurface2, scoreRect2 = MEDIAN_FONT.render(f"{self.__greenScore}", FONT_COLOR)
        self.__scoreUI.blit(
            scoreSurface2,
            (
                self.__scoreUI.get_width() / 2
                + 100
                + self.__greenTank.surface.get_width()
                - scoreRect2.width / 2,
                PLOT_HEIGHT / 2 - scoreRect2.height / 2,
            ),
        )
        self.__isScoreChanged = False

    def updateGameMenu(self, delta: float):
        self.__gameMenu.update(delta)
        if self.__gameMenu.isMenuShow and not EventManager.isTimerPaused():
            EventManager.pauseTimer()
        elif not self.__gameMenu.isMenuShow and EventManager.isTimerPaused():
            EventManager.resumeTimer()

    def onEntered(self):
        # EventManager.addHandler(TANK_REMOVED_EVENT_TYPE, self.onTankRemoved)
        ...

    def onLeaved(self):
        # EventManager.removeHandler(TANK_REMOVED_EVENT_TYPE, self.onTankRemoved)
        self.unregisterEvents()
        self.gameObjectSpace.clearObjects()
        if self.gameItemManager is not None:
            self.gameItemManager.cancelGenerate()

    def __trySendKeyEvent(self, event: Event):
        if OnlineManager.isConnected() and OnlineManager.isClient():
            if event.type == KEYDOWN:
                OnlineManager.sendEvent(ONLINE_KEYDOWN_EVENT_TYPE, {"key": event.key})
            elif event.type == KEYUP:
                OnlineManager.sendEvent(ONLINE_KEYUP_EVENT_TYPE, {"key": event.key})



    def __onGameLoaded(self, _: None):
        self.__isGameOver = False
        self.__isLoaded = True
        if self.gameItemManager is not None:
            self.gameItemManager.startGenerate()
