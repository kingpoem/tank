from loguru import logger
from pygame import Surface
import pygame
from pygame.event import Event
from pygame.freetype import Font

# from game.gameLoop import GameLoop
from game.eventManager import EventManager
from game.gameObjectManager import GameObjectManager
from game.map import MARGIN_X, MARGIN_Y, PLOT_HEIGHT, PLOT_WIDTH, Map
from game.player import Player, PlayerOperation
from game.resources import BACKGROUND, FONT_COLOR
from game.scene import Scene
from game.tank import TANK_STYLE, Tank

# 常量
MAP_WIDTH = 31
MAP_HEIGHT = 25

SCORE_UI_HEIGHT = 192


class GameScene(Scene):

    __gameObjectManager: GameObjectManager

    map: Map

    __redScore : int = 0
    __greenScore : int = 0
    scoreUI: Surface

    __font: Font

    __red_tank: Tank
    __green_tank: Tank

    __player1: Player
    __player2: Player


    __isGameOver : bool = False
    GAME_OVER_EVENT_TYPE: int = EventManager.allocateEventType()

    def __init__(self):
        logger.debug("游戏场景初始化")

        self.__gameObjectManager = GameObjectManager()

        self.__font = Font("C:\\Windows\\fonts\\msyh.ttc", 24)

        self.__initMap()
        self.__initTank()

        self.scoreUI = pygame.Surface((MAP_WIDTH * PLOT_WIDTH, SCORE_UI_HEIGHT))
        
        # 决定渲染顺序
        self.__gameObjectManager.registerObject(self.map)
        self.__gameObjectManager.registerObject(self.__red_tank)
        self.__gameObjectManager.registerObject(self.__green_tank)

        logger.debug("游戏场景初始化完成")

    def __initMap(self):
        # 地图初始化
        self.map = Map(MAP_WIDTH, MAP_HEIGHT)

    def __initTank(self):
        # 坦克初始化
        self.__red_tank = Tank(
            MARGIN_X + PLOT_WIDTH, MARGIN_Y + PLOT_HEIGHT, TANK_STYLE.RED, self.__gameObjectManager
        )
        self.__green_tank = Tank(
            MARGIN_X + PLOT_WIDTH * (MAP_WIDTH - 1),
            MARGIN_Y + PLOT_HEIGHT * (MAP_HEIGHT - 1),
            TANK_STYLE.GREEN,
            self.__gameObjectManager,
        )

        self.__player1 = Player(
            self.__red_tank,
            PlayerOperation(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g),
        )
        self.__player2 = Player(
            self.__green_tank,
            PlayerOperation(
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_KP_0
            ),
        )

    def process(self, event: Event):
        if event.type == self.GAME_OVER_EVENT_TYPE:
            if self.__gameObjectManager.containObject(self.__red_tank):
                self.__redScore += 1
            if self.__gameObjectManager.containObject(self.__green_tank):
                self.__greenScore += 1
            EventManager.cancelTimer(self.GAME_OVER_EVENT_TYPE)
            self.__gameObjectManager.removeObject(self.map)
            self.__gameObjectManager.removeObject(self.__red_tank)
            self.__gameObjectManager.removeObject(self.__green_tank)
            self.__initMap()
            self.__initTank()
            self.__gameObjectManager.registerObject(self.map)
            self.__gameObjectManager.registerObject(self.__red_tank)
            self.__gameObjectManager.registerObject(self.__green_tank)
            self.__isGameOver = False
        pass

    def update(self, delta: float):
        if (
            self.__isGameOver is False and
            (self.__gameObjectManager.containObject(self.__red_tank) is False
            or self.__gameObjectManager.containObject(self.__green_tank) is False)
        ):
            self.__isGameOver = True
            EventManager.setTimer(self.GAME_OVER_EVENT_TYPE, 3000)
        self.__player1.move(delta)
        self.__player2.move(delta)
        pass

    def render(self, screen: Surface):
        self.__gameObjectManager.renderObjects(screen)
        self.scoreUI.fill(BACKGROUND)
        self.scoreUI.blit(
            self.__red_tank.surface,
            (
                MAP_WIDTH * PLOT_WIDTH / 2 - 100 - self.__red_tank.surface.get_width() / 2,
                PLOT_HEIGHT / 2 - self.__red_tank.surface.get_height() / 2,
            ),
        )
        self.scoreUI.blit(
            self.__green_tank.surface,
            (
                MAP_WIDTH * PLOT_WIDTH / 2 + 100 - self.__green_tank.surface.get_width() / 2,
                PLOT_HEIGHT / 2 - self.__green_tank.surface.get_height() / 2,
            ),
        )
        scoreSurface1, scoreRect1 = self.__font.render(f"{self.__redScore}", FONT_COLOR)
        self.scoreUI.blit(
            scoreSurface1,
            (
                MAP_WIDTH * PLOT_WIDTH / 2
                - 100
                + self.__red_tank.surface.get_width()
                - scoreRect1.width / 2,
                PLOT_HEIGHT / 2 - scoreRect1.height / 2,
            ),
        )
        scoreSurface2, scoreRect2 = self.__font.render(f"{self.__greenScore}", FONT_COLOR)
        self.scoreUI.blit(
            scoreSurface2,
            (
                MAP_WIDTH * PLOT_WIDTH / 2
                + 100
                + self.__green_tank.surface.get_width()
                - scoreRect2.width / 2,
                PLOT_HEIGHT / 2 - scoreRect2.height / 2,
            ),
        )
        screen.blit(self.scoreUI, (MARGIN_X, MARGIN_Y + MAP_HEIGHT * PLOT_HEIGHT))
        pass
