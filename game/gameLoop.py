import sys
from loguru import logger
import pygame
import pygame.freetype


from game import player
from game.eventManager import EventManager
from game.gameObjectManager import GameObjectManager
from game.tank import TANK_STYLE, Tank
from game.map import PLOT_HEIGHT, PLOT_WIDTH, Map, OFFEST_X, OFFEST_Y
from game.gameSpace import GameSpace
from pymunk.pygame_util import DrawOptions


# 游戏是否在运行中
isRunning: bool = True
# 帧间隔
delta: float = 0
# FPS
fps: float = 0
# 坦克
red_tank: Tank | None = None
green_tank: Tank | None = None


def runLoop():
    global isRunning, delta, fps, red_tank

    # 常量
    MAP_WIDTH = 31
    MAP_HEIGHT = 25

    FPS = 60

    BACKGROUND = (255, 255, 255)
    FONT_COLOR = (0, 0, 0)

    # 配置基础环境

    # 开始初始化
    pygame.init()

    # 初始化游戏屏幕
    screen = pygame.display.set_mode(
        (
            OFFEST_X * 2 + MAP_WIDTH * PLOT_WIDTH,
            OFFEST_Y * 2 + MAP_HEIGHT * PLOT_HEIGHT,
        ),
        # pygame.RESIZABLE,
    )
    pygame.display.set_caption("Tank Game")
    draw_options = DrawOptions(screen)

    # 初始化渲染字体
    font = pygame.freetype.Font("C:\\Windows\\fonts\\msyh.ttc", 24)

    # 初始化游戏时钟
    clock = pygame.time.Clock()

    # 初始化物理世界
    GameSpace.initSpace()

    # 地图初始化
    map = Map(MAP_WIDTH, MAP_HEIGHT)
    GameObjectManager.registerObject(map)

    # 坦克初始化
    red_tank = Tank(OFFEST_X + PLOT_WIDTH, OFFEST_Y + PLOT_HEIGHT, TANK_STYLE.RED)
    green_tank = Tank(
        OFFEST_X + PLOT_WIDTH * (MAP_WIDTH - 1), OFFEST_Y + PLOT_HEIGHT * (MAP_HEIGHT - 1), TANK_STYLE.GREEN
    )
    GameObjectManager.registerObject(red_tank)
    GameObjectManager.registerObject(green_tank)
    player1 = player.Player(
        red_tank,
        player.PlayerOperation(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_g),
    )
    player2 = player.Player(
        green_tank,
        player.PlayerOperation(
            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_KP_0
        ),
    )

    while isRunning:
        clock.tick(FPS)
        fps = clock.get_fps()
        if fps != 0:
            delta = 1 / fps

        __handleEvent()
        if not isRunning:
            __onGameQuit()
            break
        player1.move(delta)
        player2.move(delta)
        # 更新物理世界
        GameSpace.updateSpace(delta)

        screen.fill(BACKGROUND)

        # 地图渲染
        # gameSpace.spaceInstance.debug_draw(draw_options)

        GameObjectManager.drawObjects(screen)
        # debug
        # FPS
        font.render_to(screen, (0, 0), f"FPS: {fps:.2f}", FONT_COLOR)
        # delta
        font.render_to(screen, (0, 24), f"delta: {delta * 1000:.1f}ms", FONT_COLOR)
        pygame.display.update()

    pygame.quit()

    logger.info("游戏退出")

    sys.exit()


def __handleEvent():
    global isRunning
    events = pygame.event.get()
    for event in events:
        EventManager.handleEvent(event)
        match event.type:
            case pygame.QUIT:
                isRunning = False
            case _:
                # 处理剩余的事件
                pass

    pass


def __onGameQuit():
    pass
