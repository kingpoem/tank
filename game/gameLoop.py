import os
import sys
from loguru import logger
import pygame
import pygame.freetype

from pygame import Surface


from game.eventManager import EventManager
from game.resources import BACKGROUND, FONT_COLOR
from game.gameSpace import GameSpace
from pymunk.pygame_util import DrawOptions

from game.sceneManager import SceneManager


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


    __debugOptions : DrawOptions

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

        # 初始化场景
        SceneManager.init()

        GameLoop.screen = pygame.display.set_mode(
            SceneManager.getCurrentScene().uiSize,
            # pygame.NOFRAME,
        )
        

        pygame.display.set_caption("Tank Game")

        GameLoop.__debugOptions = DrawOptions(GameLoop.screen)

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

        GameLoop.screen.fill(BACKGROUND)
        while GameLoop.isRunning:
            
            GameLoop.fps = clock.get_fps()
            if GameLoop.fps != 0:
                GameLoop.delta = 1 / GameLoop.fps

            GameLoop.__handleEvent()
            if not GameLoop.isRunning:
                GameLoop.__onGameQuit()
                break

            # 更新物理世界
            GameSpace.updateSpace(GameLoop.delta)
            SceneManager.getCurrentScene().update(GameLoop.delta)

            SceneManager.getCurrentScene().render(GameLoop.screen)
            # if (space := GameSpace.getSpace()) is not None:
            #     space.debug_draw(GameLoop.__debugOptions)

            # debug
            # FPS
            GameLoop.font.render_to(GameLoop.screen, (0, 0), f"FPS: {GameLoop.fps:.2f}", FONT_COLOR)
            # delta
            GameLoop.font.render_to(
                GameLoop.screen, (0, 24), f"delta: {GameLoop.delta * 1000:.1f}ms", FONT_COLOR
            )
            pygame.display.flip()

            clock.tick(FPS)
        pygame.quit()
        logger.info("游戏退出")

    @staticmethod
    def __handleEvent():
        events = pygame.event.get()
        for event in events:
            EventManager.handleEvent(event)
            SceneManager.getCurrentScene().process(event)
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
