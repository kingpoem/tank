from random import randint, choice
from enum import Enum

from pygame import Surface, draw, gfxdraw
import pygame
from pymunk import Body, Segment, Shape, Space, Poly

from game.gameObject import GameObject
from game.resources import BACKGROUND
from structs.map import MAP_PLOT_TYPE, Map



MAP_MAX_WIDTH = 25
MAP_MAX_HEIGHT = 19

MAP_MIN_WIDTH = 9
MAP_MIN_HEIGHT = 7

# 地图边距
MARGIN_X = 40
MARGIN_Y = 40

# 地图格子尺寸
PLOT_WIDTH = 50
PLOT_HEIGHT = 50

# 墙的宽度
WALL_WIDTH = 10


# 游戏地图类
class GameMap(GameObject):

    __map : Map

    @property
    def width(self):
        return self.__map.width
    @property
    def height(self):
        return self.__map.height
    
    @property
    def map(self):
        return self.__map

    def __init__(self, width: int, height: int):
        self.__map = Map(width, height)

        self.surface = pygame.Surface(
            (MARGIN_X * 2 + PLOT_WIDTH * width, MARGIN_Y * 2 + PLOT_HEIGHT * height)
        )
        self.surface.fill(BACKGROUND)

        def __getUpRectPoints(basePoint: tuple[float, float]) -> list[tuple[float, float]]:
            return [
                (basePoint[0] + WALL_WIDTH / 2, basePoint[1] + WALL_WIDTH / 2),
                (basePoint[0] - WALL_WIDTH / 2, basePoint[1] + WALL_WIDTH / 2),
                (basePoint[0] - WALL_WIDTH / 2, basePoint[1] - PLOT_HEIGHT / 2),
                (basePoint[0] + WALL_WIDTH / 2, basePoint[1] - PLOT_HEIGHT / 2),
            ]

        def __getDownRectPoints(basePoint: tuple[float, float]) -> list[tuple[float, float]]:
            return [
                (basePoint[0] - WALL_WIDTH / 2, basePoint[1] - WALL_WIDTH / 2),
                (basePoint[0] + WALL_WIDTH / 2, basePoint[1] - WALL_WIDTH / 2),
                (basePoint[0] + WALL_WIDTH / 2, basePoint[1] + PLOT_HEIGHT / 2),
                (basePoint[0] - WALL_WIDTH / 2, basePoint[1] + PLOT_HEIGHT / 2),
            ]

        def __getLeftRectPoints(basePoint: tuple[float, float]) -> list[tuple[float, float]]:
            return [
                (basePoint[0] + WALL_WIDTH / 2, basePoint[1] - WALL_WIDTH / 2),
                (basePoint[0] + WALL_WIDTH / 2, basePoint[1] + WALL_WIDTH / 2),
                (basePoint[0] - PLOT_WIDTH / 2, basePoint[1] + WALL_WIDTH / 2),
                (basePoint[0] - PLOT_WIDTH / 2, basePoint[1] - WALL_WIDTH / 2),
            ]

        def __getRightRectPoints(basePoint: tuple[float, float]) -> list[tuple[float, float]]:
            return [
                (basePoint[0] - WALL_WIDTH / 2, basePoint[1] - WALL_WIDTH / 2),
                (basePoint[0] - WALL_WIDTH / 2, basePoint[1] + WALL_WIDTH / 2),
                (basePoint[0] + PLOT_WIDTH / 2, basePoint[1] + WALL_WIDTH / 2),
                (basePoint[0] + PLOT_WIDTH / 2, basePoint[1] - WALL_WIDTH / 2),
            ]

        for x in range(self.width):
            for y in range(self.height):
                if self.__map[x, y] == MAP_PLOT_TYPE.MAP_BLOCK:
                    basePoint = (
                        MARGIN_X + x * PLOT_WIDTH + PLOT_WIDTH / 2,
                        MARGIN_Y + y * PLOT_HEIGHT + PLOT_HEIGHT / 2,
                    )
                    # pygame.draw.circle(self.surface,(255,0,0),basePoint,int(WALL_WIDTH))
                    # 向上
                    if y != 0 and self.__map[x, y - 1] == MAP_PLOT_TYPE.MAP_BLOCK:
                        gfxdraw.filled_polygon(
                            self.surface,
                            __getUpRectPoints(basePoint),
                            (0, 0, 0),
                        )
                    if y != self.height - 1 and self.__map[x, y + 1] == MAP_PLOT_TYPE.MAP_BLOCK:
                        gfxdraw.filled_polygon(
                            self.surface,
                            __getDownRectPoints(basePoint),
                            (0, 0, 0),
                        )
                    # 向左
                    if x != 0 and self.__map[x - 1, y] == MAP_PLOT_TYPE.MAP_BLOCK:
                        gfxdraw.filled_polygon(
                            self.surface,
                            __getLeftRectPoints(basePoint),
                            (0, 0, 0),
                        )
                    if x != self.width - 1 and self.__map[x + 1, y] == MAP_PLOT_TYPE.MAP_BLOCK:
                        gfxdraw.filled_polygon(
                            self.surface,
                            __getRightRectPoints(basePoint),
                            (0, 0, 0),
                        )
        self.body = Body(body_type=Body.STATIC)
        self.shapes = []
        for x in range(self.width):
            for y in range(self.height):
                if self.__map[x, y] == MAP_PLOT_TYPE.MAP_BLOCK:
                    basePoint = (
                        MARGIN_X + x * PLOT_WIDTH + PLOT_WIDTH / 2,
                        MARGIN_Y + y * PLOT_HEIGHT + PLOT_HEIGHT / 2,
                    )

                    # 向上
                    if y != 0 and self.__map[x, y - 1] == MAP_PLOT_TYPE.MAP_BLOCK:
                        self.shapes.append(
                            Poly(
                                self.body,
                                [
                                    (
                                        basePoint[0] - WALL_WIDTH / 2,
                                        basePoint[1] + WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] + WALL_WIDTH / 2,
                                        basePoint[1] + WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] - WALL_WIDTH / 2,
                                        basePoint[1] - PLOT_HEIGHT - WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] + WALL_WIDTH / 2,
                                        basePoint[1] - PLOT_HEIGHT - WALL_WIDTH / 2,
                                    ),
                                ],
                            )
                        )
                    if y != self.height - 1 and self.__map[x, y + 1] == MAP_PLOT_TYPE.MAP_BLOCK:
                        self.shapes.append(
                            Poly(
                                self.body,
                                [
                                    (
                                        basePoint[0] - WALL_WIDTH / 2,
                                        basePoint[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] + WALL_WIDTH / 2,
                                        basePoint[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] - WALL_WIDTH / 2,
                                        basePoint[1] + PLOT_HEIGHT + WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] + WALL_WIDTH / 2,
                                        basePoint[1] + PLOT_HEIGHT + WALL_WIDTH / 2,
                                    ),
                                ],
                            )
                        )
                    # 向左
                    if x != 0 and self.__map[x - 1, y] == MAP_PLOT_TYPE.MAP_BLOCK:
                        self.shapes.append(
                            Poly(
                                self.body,
                                [
                                    (
                                        basePoint[0] + WALL_WIDTH / 2,
                                        basePoint[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] + WALL_WIDTH / 2,
                                        basePoint[1] + WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] - PLOT_WIDTH - WALL_WIDTH / 2,
                                        basePoint[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] - PLOT_WIDTH - WALL_WIDTH / 2,
                                        basePoint[1] + WALL_WIDTH / 2,
                                    ),
                                ],
                            )
                        )
                    if x != self.width - 1 and self.__map[x + 1, y] == MAP_PLOT_TYPE.MAP_BLOCK:
                        self.shapes.append(
                            Poly(
                                self.body,
                                [
                                    (
                                        basePoint[0] - WALL_WIDTH / 2,
                                        basePoint[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] - WALL_WIDTH / 2,
                                        basePoint[1] + WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] + PLOT_WIDTH + WALL_WIDTH / 2,
                                        basePoint[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        basePoint[0] + PLOT_WIDTH + WALL_WIDTH / 2,
                                        basePoint[1] + WALL_WIDTH / 2,
                                    ),
                                ],
                            )
                        )
        for shape in self.shapes:
            shape.elasticity = 1
            shape.friction = 1

    def getPlotPos(self,x : int,y : int):
        return (
            MARGIN_X + x * PLOT_WIDTH + PLOT_WIDTH / 2,
            MARGIN_Y + y * PLOT_HEIGHT + PLOT_HEIGHT / 2,
        )
    # 绘制迷宫函数
    def render(self, screen: Surface):
        screen.blit(self.surface, (0, 0))
