from abc import ABC, abstractmethod
import math
from random import randint
import random
from typing import Sequence
from loguru import logger
from pygame import K_DOWN, K_ESCAPE, KEYDOWN, QUIT, Rect, Surface
import pygame
from pygame import transform
from pygame.event import Event
from pygame.freetype import Font
from pymunk import Space

# from game.gameLoop import GameLoop
from game.controls.floatMenu import FloatMenu
from game.controls.selectionControl import Selection, SelectionControl
from game.defines import BACKGROUND, FONT_COLOR, MEDIAN_FONT, SELECTION_HEIGHT
from game.operateable import Operateable, Operation
from game.sceneManager import SCENE_TYPE, SceneManager
from game.spaces.gameObjectSpace import GameObjectSpace
from game.eventManager import EventManager
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
from game.scenes.scene import Scene
from game.tank import TANK_REMOVED_EVENT_TYPE, Tank


SCORE_UI_HEIGHT = 192
GAME_OVER_EVENT_TYPE: int = EventManager.allocateEventType()
START_NEW_TURN_EVENT_TYPE: int = EventManager.allocateEventType()
GAME_MAP_UI_MAX_WIDTH = MAP_MAX_WIDTH * PLOT_WIDTH + MARGIN_X * 2
GAME_MAP_UI_MAX_HEIGHT = MAP_MAX_HEIGHT * PLOT_HEIGHT + MARGIN_Y * 2


class GameScene(Scene, ABC):

    __gameObjectSpace: GameObjectSpace
    __gameItemManager: GameItemManager

    __gameMap: GameMap

    __redScore: int = 0
    __greenScore: int = 0

    __ui: Surface
    __gameMapUI: Surface
    __scoreUI: Surface
    __gameMenu: FloatMenu

    __redTank: Tank
    __greenTank: Tank
    __isGameOver: bool = False

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

    def __init__(self, gameObjectSpace: GameObjectSpace):
        self.__gameObjectSpace = gameObjectSpace
        self.__gameMap = self.generateMap()
        self.__redTank, self.__greenTank = self.generateTanks()
        self.__gameItemManager = GameItemManager(self.__gameMap)
        self.__gameMapUI = pygame.Surface(
            (
                self.__gameMap.width * PLOT_WIDTH + MARGIN_X * 2,
                self.__gameMap.height * PLOT_HEIGHT + MARGIN_Y * 2,
            )
        )
        self.__scoreUI = pygame.Surface((GAME_MAP_UI_MAX_WIDTH, SCORE_UI_HEIGHT))
        self.__ui = pygame.Surface(
            (
                GAME_MAP_UI_MAX_WIDTH,
                GAME_MAP_UI_MAX_HEIGHT + self.__scoreUI.get_height(),
            )
        )
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
        # 决定渲染顺序
        self.__gameObjectSpace.registerObject(self.__gameMap)
        self.__gameObjectSpace.registerObject(self.__redTank)
        self.__gameObjectSpace.registerObject(self.__greenTank)

        logger.debug("游戏场景初始化完成")

    @abstractmethod
    def startNewTurn(self) -> bool:
        """
        开始新一轮游戏
        返回值False则代表开始最后一轮，之后不在重新开始
        """
        ...

    @abstractmethod
    def generateMap(self) -> GameMap: ...

    @abstractmethod
    def generateTanks(self) -> Sequence[Tank]: ...

    def isGameMenuPauseGame(self) -> bool:
        return True

    def process(self, event: Event):
        if self.__gameMenu.isMenuShow:
            self.__gameMenu.process(event)
            if self.isGameMenuPauseGame() or self.__gameMenu.isMenuShow is False:
                return

        if event.type == GAME_OVER_EVENT_TYPE:
            self.onGameOvered()
            # TODO 最终结束画面
        elif event.type == START_NEW_TURN_EVENT_TYPE:
            self.__isGameOver = False
        elif event.type == TANK_REMOVED_EVENT_TYPE:
            self.onTankRemoved(event.dict["tank"])
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if self.__gameMenu.isMenuShow is False:
                    self.__gameMenu.show()

    def update(self, delta: float):
        # if self.__isGameOver is False and (
        #     self.__gameObjectSpace.containObject(self.__redTank) is False
        #     or self.__gameObjectSpace.containObject(self.__greenTank) is False
        # ):
        #     self.__isGameOver = True
        #     EventManager.setTimer(GAME_OVER_EVENT_TYPE, 3000, 1)

        if self.__gameMenu.isMenuShow is False or not self.isGameMenuPauseGame():
            self.__gameObjectSpace.updateObjects(delta)
        # 更新画面
        self.updateGameMap(delta)
        self.updateScoreBoard(delta)
        self.updateGameMenu(delta)

    def updateGameMap(self, delta: float):
        self.__gameMapUI.fill(BACKGROUND)
        self.__gameObjectSpace.renderObjects(self.__gameMapUI)

    def updateScoreBoard(self, delta: float):
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
        self.__ui.fill(BACKGROUND)
        scale_map = transform.smoothscale_by(
            self.__gameMapUI,
            min(
                GAME_MAP_UI_MAX_WIDTH / self.__gameMapUI.get_width(),
                GAME_MAP_UI_MAX_HEIGHT / self.__gameMapUI.get_height(),
            ),
        )
        self.__ui.blit(
            scale_map,
            scale_map.get_rect(center=(GAME_MAP_UI_MAX_WIDTH / 2,GAME_MAP_UI_MAX_HEIGHT / 2)),
        )
        self.__ui.blit(self.__scoreUI, (0, GAME_MAP_UI_MAX_HEIGHT))

    def updateGameMenu(self, delta: float):
        self.__gameMenu.update(delta)
        if self.isGameMenuPauseGame():
            if self.__gameMenu.isMenuShow and not EventManager.isTimerPaused():
                EventManager.pauseTimer()
            elif not self.__gameMenu.isMenuShow and EventManager.isTimerPaused():
                EventManager.resumeTimer()

    def onEntered(self):
        # EventManager.addHandler(TANK_REMOVED_EVENT_TYPE, self.onTankRemoved)
        ...

    def onLeaved(self):
        # EventManager.removeHandler(TANK_REMOVED_EVENT_TYPE, self.onTankRemoved)
        ...

    def onGameOvered(self):
        if self.gameObjectSpace.containObject(self.redTank):
            self.__redScore += 1
        if self.gameObjectSpace.containObject(self.greenTank):
            self.__greenScore += 1
        if self.startNewTurn():
            self.__gameMapUI = pygame.Surface(
                (
                    self.__gameMap.width * PLOT_WIDTH + MARGIN_X * 2,
                    self.__gameMap.height * PLOT_HEIGHT + MARGIN_Y * 2,
                )
            )
            EventManager.raiseEventType(START_NEW_TURN_EVENT_TYPE)

    def onTankRemoved(self, tank: Tank):
        if self.__isGameOver:
            return
        self.__isGameOver = True
        EventManager.setTimer(GAME_OVER_EVENT_TYPE, 3000, 1)
