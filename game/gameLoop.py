import os
import sys
from loguru import logger
import pygame
import pygame.freetype

from pygame import Surface

from game import player
from game.eventManager import EventManager
from game.gameObjectManager import GameObjectManager
from game.gameScene import GameScene
from game.resources import BACKGROUND, FONT_COLOR
from game.tank import TANK_STYLE, Tank
from game.map import PLOT_HEIGHT, PLOT_WIDTH, Map, MARGIN_X, MARGIN_Y
from game.gameSpace import GameSpace
from pymunk.pygame_util import DrawOptions


FPS = 60


class GameLoop:

    isRunning: bool = False
    """游戏是否在运行中"""

    delta: float = 0
    """帧间隔"""

    fps: float = 0
    """FPS"""

    screen: Surface
    """绘制屏幕"""

    font: pygame.freetype.Font
    """字体"""

    gameScene: GameScene
    """游戏场景"""

    def __init__(self):
        raise NotImplementedError("GameLoop是静态类不允许实例化")

    @staticmethod
    def __initGame():
        logger.info("初始化游戏")

        # 初始化 pygame
        pygame.init()

        # 初始化游戏屏幕
        GameLoop.screen = pygame.display.set_mode((1920,1080))

        # 初始化渲染字体
        GameLoop.font = pygame.freetype.Font("C:\\Windows\\fonts\\msyh.ttc", 24)

        # 初始化物理世界
        GameSpace.initSpace()

        GameLoop.gameScene = GameScene()

        GameLoop.screen = pygame.display.set_mode(
            (
                GameLoop.gameScene.map.surface.get_width(),
                GameLoop.gameScene.map.surface.get_height()
                + GameLoop.gameScene.scoreUI.get_height(),
            ),
            # pygame.NOFRAME,
        )
        

        pygame.display.set_caption("Tank Game")

    @staticmethod
    def run():
        """
        开始游戏循环
        """
        if GameLoop.isRunning:
            return
        GameLoop.isRunning = True

        # 配置基础环境

        # 开始初始化
        GameLoop.__initGame()

        # 初始化游戏时钟
        clock = pygame.time.Clock()

        while GameLoop.isRunning:
            clock.tick(FPS)
            GameLoop.fps = clock.get_fps()
            if GameLoop.fps != 0:
                GameLoop.delta = 1 / GameLoop.fps

            GameLoop.__handleEvent()
            if not GameLoop.isRunning:
                GameLoop.__onGameQuit()
                break

            # 更新物理世界
            GameSpace.updateSpace(GameLoop.delta)
            GameLoop.gameScene.update(GameLoop.delta)

            GameLoop.screen.fill(BACKGROUND)
            GameLoop.gameScene.render(GameLoop.screen)

            # debug
            # FPS
            GameLoop.font.render_to(GameLoop.screen, (0, 0), f"FPS: {GameLoop.fps:.2f}", FONT_COLOR)
            # delta
            GameLoop.font.render_to(
                GameLoop.screen, (0, 24), f"delta: {GameLoop.delta * 1000:.1f}ms", FONT_COLOR
            )
            pygame.display.update()

        pygame.quit()
        logger.info("游戏退出")

    @staticmethod
    def __handleEvent():
        events = pygame.event.get()
        for event in events:
            EventManager.handleEvent(event)
            GameLoop.gameScene.process(event)
            match event.type:
                case pygame.QUIT:
                    GameLoop.isRunning = False
                case _:
                    # 处理剩余的事件
                    pass

        pass

    @staticmethod
    def __onGameQuit():
        pass
