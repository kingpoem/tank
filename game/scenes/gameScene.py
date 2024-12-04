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
from game.controls.selectionMenu import Selection, SelectionMenu
from game.operateable import Operateable, Operation
from game.sceneManager import SCENE_TYPE, SceneManager
from game.weapons.commonWeapon import CommonWeapon
from game.eventManager import EventManager
from game.gameItems.gameItem import GameItem
from game.gameItemManager import GameItemManager
from game.gameObjectManager import GameObjectManager
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
from game.gameResources import BACKGROUND, FONT_COLOR, MENU_BACKGROUND, easeLinear
from game.scenes.scene import Scene
from game.tank import TANK_STYLE, Tank
from game.weapons.weaponFactory import WEAPON_TYPE, WeaponFactory


SCORE_UI_HEIGHT = 192


class GameScene(Scene):

    __gameObjectManager: GameObjectManager
    __gameItemManager: GameItemManager

    __gameMap: GameMap

    __redScore: int = 0
    __greenScore: int = 0

    __ui: Surface
    __gameMapUI: Surface
    __scoreUI: Surface
    __gameMenu: SelectionMenu

    __font: Font

    __red_tank: Tank
    __green_tank: Tank

    __isGameOver: bool = False
    GAME_OVER_EVENT_TYPE: int = EventManager.allocateEventType()

    @property
    def ui(self) -> Surface:
        return self.__ui

    @property
    def gameObjectManager(self) -> GameObjectManager | None:
        return self.__gameObjectManager

    def __init__(self):
        logger.debug("游戏场景初始化")
        space = Space()
        # 物体每秒保留多少速度
        space.damping = 0
        self.__gameObjectManager = GameObjectManager(space)

        self.__font = Font("C:\\Windows\\fonts\\msyh.ttc", 24)

        self.__initMap()
        self.__initTank()

        self.__gameItemManager = GameItemManager(self.__gameMap, self.__gameObjectManager)
        self.__gameMapUI = pygame.Surface(
            (MAP_MAX_WIDTH * PLOT_WIDTH + MARGIN_X * 2, MAP_MAX_HEIGHT * PLOT_HEIGHT + MARGIN_Y * 2)
        )
        self.__scoreUI = pygame.Surface((self.__gameMapUI.get_width(), SCORE_UI_HEIGHT))
        self.__ui = pygame.Surface(
            (
                self.__gameMapUI.get_width(),
                self.__gameMapUI.get_height() + self.__scoreUI.get_height(),
            )
        )

        self.__gameMenu = SelectionMenu(
            self.__ui,
            1080,
            480,
            [
                Selection(
                    lambda: "返回主菜单", lambda: SceneManager.changeScene(SCENE_TYPE.START_SCENE)
                ),
                Selection(lambda: "退出游戏", lambda: EventManager.raiseEventType(QUIT)),
            ],
        )

        # 决定渲染顺序
        self.__gameObjectManager.registerObject(self.__gameMap)
        self.__gameObjectManager.registerObject(self.__red_tank)
        self.__gameObjectManager.registerObject(self.__green_tank)
        # self.__gameObjectManager.registerObject(GameItem(PLOT_WIDTH, PLOT_HEIGHT))

        logger.debug("游戏场景初始化完成")

    def __initMap(self):
        # 地图初始化
        width = randint(MAP_MIN_WIDTH // 2, MAP_MAX_WIDTH // 2) * 2 + 1
        height = randint(MAP_MIN_HEIGHT // 2, MAP_MAX_HEIGHT // 2) * 2 + 1
        self.__gameMap = GameMap(width, height)
        self.__gameObjectManager.spaceRegion = Rect(
            0, 0, self.__gameMap.surface.get_width(), self.__gameMap.surface.get_height()
        )

    def __initTank(self):
        # 坦克初始化
        pos = self.__gameMap.getPlotPos(1, 1)
        self.__red_tank = Tank(
            pos[0],
            pos[1],
            TANK_STYLE.RED,
            Operation(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g),
        )
        pos = self.__gameMap.getPlotPos(self.__gameMap.width - 2, self.__gameMap.height - 2)
        self.__green_tank = Tank(
            pos[0],
            pos[1],
            TANK_STYLE.GREEN,
            Operation(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_KP_0),
        )
        # # 添加一点随机位置角度偏移
        self.__red_tank.body.angle = random.uniform(0, math.pi)
        self.__red_tank.body.position += (random.uniform(-5, 5), random.uniform(-5, 5))

        self.__green_tank.body.angle = random.uniform(0, math.pi)
        self.__green_tank.body.position += (random.uniform(-5, 5), random.uniform(-5, 5))

        self.__red_tank.weapon = WeaponFactory.createWeapon(
            self.__red_tank, WEAPON_TYPE.MISSILE_WEAPON
        )
        self.__green_tank.weapon = WeaponFactory.createWeapon(
            self.__green_tank, WEAPON_TYPE.COMMON_WEAPON
        )

    def process(self, event: Event):
        if self.__gameMenu.isMenuShow:
            self.__gameMenu.process(event)
            return

        if event.type == self.GAME_OVER_EVENT_TYPE:
            if self.__gameObjectManager.containObject(self.__red_tank):
                self.__redScore += 1
            if self.__gameObjectManager.containObject(self.__green_tank):
                self.__greenScore += 1
            EventManager.cancelTimer(self.GAME_OVER_EVENT_TYPE)
            self.__gameObjectManager.clearObjects()
            self.__initMap()
            self.__initTank()
            self.__gameItemManager.reset(self.__gameMap, self.__gameObjectManager)
            self.__gameObjectManager.registerObject(self.__gameMap)
            self.__gameObjectManager.registerObject(self.__red_tank)
            self.__gameObjectManager.registerObject(self.__green_tank)
            self.__isGameOver = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.__gameMenu.show()

    def update(self, delta: float):
        if self.__isGameOver is False and (
            self.__gameObjectManager.containObject(self.__red_tank) is False
            or self.__gameObjectManager.containObject(self.__green_tank) is False
        ):
            self.__isGameOver = True
            EventManager.setTimer(self.GAME_OVER_EVENT_TYPE, 3000)

        # 当打开游戏菜单时，不更新物体
        if self.__gameMenu.isMenuShow is False:
            self.__gameObjectManager.updateObjects(delta)
        # 更新画面
        self.__updateGameMap(delta)
        self.__updateScoreBoard(delta)
        self.__updateGameMenu(delta)

    def __updateGameMap(self, delta: float):
        self.__gameMapUI.fill(BACKGROUND)
        self.__gameObjectManager.renderObjects(self.__gameMapUI)

    def __updateScoreBoard(self, delta: float):
        self.__scoreUI.fill(BACKGROUND)
        self.__scoreUI.blit(
            self.__red_tank.surface,
            (
                self.__scoreUI.get_width() / 2 - 100 - self.__red_tank.surface.get_width() / 2,
                PLOT_HEIGHT / 2 - self.__red_tank.surface.get_height() / 2,
            ),
        )
        self.__scoreUI.blit(
            self.__green_tank.surface,
            (
                self.__scoreUI.get_width() / 2 + 100 - self.__green_tank.surface.get_width() / 2,
                PLOT_HEIGHT / 2 - self.__green_tank.surface.get_height() / 2,
            ),
        )
        scoreSurface1, scoreRect1 = self.__font.render(f"{self.__redScore}", FONT_COLOR)
        self.__scoreUI.blit(
            scoreSurface1,
            (
                self.__scoreUI.get_width() / 2
                - 100
                + self.__red_tank.surface.get_width()
                - scoreRect1.width / 2,
                PLOT_HEIGHT / 2 - scoreRect1.height / 2,
            ),
        )
        scoreSurface2, scoreRect2 = self.__font.render(f"{self.__greenScore}", FONT_COLOR)
        self.__scoreUI.blit(
            scoreSurface2,
            (
                self.__scoreUI.get_width() / 2
                + 100
                + self.__green_tank.surface.get_width()
                - scoreRect2.width / 2,
                PLOT_HEIGHT / 2 - scoreRect2.height / 2,
            ),
        )
        self.__ui.fill(BACKGROUND)
        self.__ui.blit(
            self.__gameMapUI,
            (
                (self.__gameMapUI.get_width() - self.__gameMap.surface.get_width()) / 2,
                (self.__gameMapUI.get_height() - self.__gameMap.surface.get_height()) / 2,
            ),
        )
        self.__ui.blit(self.__scoreUI, (0, self.__gameMapUI.get_height()))

    def __updateGameMenu(self, delta: float):
        self.__gameMenu.update(delta)
        if self.__gameMenu.isMenuShow and not EventManager.isTimerPaused():
            EventManager.pauseTimer()
        elif not self.__gameMenu.isMenuShow and EventManager.isTimerPaused():
            EventManager.resumeTimer()

    def onLeaved(self):
        ...