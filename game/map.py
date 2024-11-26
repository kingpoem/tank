from random import randint, choice
from enum import Enum

from pygame import Surface, draw
from pymunk import Body, Segment, Shape, Space, Poly

from game.gameObject import GameObject


OFFEST_X = 40
OFFEST_Y = 40
PLOT_WIDTH = 40
PLOT_HEIGHT = 40
WALL_WIDTH = 10


# 接受枚举类型变量
class MAP_ENTRY_TYPE(Enum):
    MAP_EMPTY = (0,)  # 可移动单元值为0
    MAP_BLOCK = (1,)  # 墙值为1


# 接受枚举类型变量
class WALL_DIRECTION(Enum):
    # 0，1，2，3分别表示左上右下
    WALL_LEFT = (0,)
    WALL_UP = (1,)
    WALL_RIGHT = (2,)
    WALL_DOWN = (3,)


# 游戏地图类
class Map(GameObject):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [
            [MAP_ENTRY_TYPE.MAP_EMPTY for x in range(self.width)] for y in range(self.height)
        ]
        # 初始化时调用 Prim 算法
        self.__doRandomPrim()

        self.body = Body(body_type=Body.STATIC)
        self.shapes = []
        for x in range(self.width):
            for y in range(self.height):
                if self.map[y][x] == 1:
                    base_point = (
                        OFFEST_X + x * PLOT_WIDTH + PLOT_WIDTH / 2,
                        OFFEST_Y + y * PLOT_HEIGHT + PLOT_HEIGHT / 2,
                    )

                    # 向上

                    if y != 0 and self.map[y - 1][x] == 1:
                        self.shapes.append(
                            Poly(
                                self.body,
                                [
                                    (
                                        base_point[0] - WALL_WIDTH / 2,
                                        base_point[1] + WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] + WALL_WIDTH / 2,
                                        base_point[1] + WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] - WALL_WIDTH / 2,
                                        base_point[1] - PLOT_HEIGHT - WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] + WALL_WIDTH / 2,
                                        base_point[1] - PLOT_HEIGHT - WALL_WIDTH / 2,
                                    ),
                                ],
                            )
                        )
                    if y != self.height - 1 and self.map[y + 1][x] == 1:
                        self.shapes.append(
                            Poly(
                                self.body,
                                [
                                    (
                                        base_point[0] - WALL_WIDTH / 2,
                                        base_point[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] + WALL_WIDTH / 2,
                                        base_point[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] - WALL_WIDTH / 2,
                                        base_point[1] + PLOT_HEIGHT + WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] + WALL_WIDTH / 2,
                                        base_point[1] + PLOT_HEIGHT + WALL_WIDTH / 2,
                                    ),
                                ],
                            )
                        )
                    # 向左
                    if x != 0 and self.map[y][x - 1] == 1:
                        self.shapes.append(
                            Poly(
                                self.body,
                                [
                                    (
                                        base_point[0] + WALL_WIDTH / 2,
                                        base_point[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] + WALL_WIDTH / 2,
                                        base_point[1] + WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] - PLOT_WIDTH - WALL_WIDTH / 2,
                                        base_point[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] - PLOT_WIDTH - WALL_WIDTH / 2,
                                        base_point[1] + WALL_WIDTH / 2,
                                    ),
                                ],
                            )
                        )
                    if x != self.width - 1 and self.map[y][x + 1] == 1:
                        self.shapes.append(
                            Poly(
                                self.body,
                                [
                                    (
                                        base_point[0] - WALL_WIDTH / 2,
                                        base_point[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] - WALL_WIDTH / 2,
                                        base_point[1] + WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] + PLOT_WIDTH + WALL_WIDTH / 2,
                                        base_point[1] - WALL_WIDTH / 2,
                                    ),
                                    (
                                        base_point[0] + PLOT_WIDTH + WALL_WIDTH / 2,
                                        base_point[1] + WALL_WIDTH / 2,
                                    ),
                                ],
                            )
                        )
        for shape in self.shapes:
            shape.elasticity = 1
            shape.friction = 1

    # 定义将整个Map的单元设置为某个值的函数
    def resetMap(self, value):
        for y in range(self.height):
            for x in range(self.width):
                self.setMap(x, y, value)  # 调用将某个单元设为某个值的函数

    # 定义将某个单元设为某个值的函数
    def setMap(self, x, y, value):
        if value == MAP_ENTRY_TYPE.MAP_EMPTY:
            self.map[y][x] = 0
        elif value == MAP_ENTRY_TYPE.MAP_BLOCK:
            self.map[y][x] = 1

    # 定义判断某个单元时候被访问的函数
    def isVisited(self, x, y):
        return self.map[y][x] == 1  # 等于1返回True，代表未被访问，不等于1返回False

    # 绘制迷宫函数
    def draw(self, screen: Surface):
        for x in range(self.width):
            for y in range(self.height):
                if self.map[y][x] == 1:
                    base_point = (
                        OFFEST_X + x * PLOT_WIDTH + PLOT_WIDTH / 2,
                        OFFEST_Y + y * PLOT_HEIGHT + PLOT_HEIGHT / 2,
                    )
                    # pygame.draw.circle(screen,(0,0,0),base_point,int(WALL_WIDTH / 2))
                    # 向上
                    if y != 0 and self.map[y - 1][x] == 1:
                        draw.line(
                            screen,
                            (0, 0, 0),
                            (base_point[0], base_point[1] + WALL_WIDTH / 2),
                            (base_point[0], base_point[1] - PLOT_HEIGHT - WALL_WIDTH / 2),
                            WALL_WIDTH,
                        )
                    if y != self.height - 1 and self.map[y + 1][x] == 1:
                        draw.line(
                            screen,
                            (0, 0, 0),
                            (base_point[0], base_point[1] - WALL_WIDTH / 2),
                            (base_point[0], base_point[1] + PLOT_HEIGHT + WALL_WIDTH / 2),
                            WALL_WIDTH,
                        )
                    # 向左
                    if x != 0 and self.map[y][x - 1] == 1:
                        draw.line(
                            screen,
                            (0, 0, 0),
                            (base_point[0] + WALL_WIDTH / 2, base_point[1]),
                            (base_point[0] - PLOT_WIDTH - WALL_WIDTH / 2, base_point[1]),
                            WALL_WIDTH,
                        )
                    if x != self.width - 1 and self.map[y][x + 1] == 1:
                        draw.line(
                            screen,
                            (0, 0, 0),
                            (base_point[0] - WALL_WIDTH / 2, base_point[1]),
                            (base_point[0] + PLOT_WIDTH + WALL_WIDTH / 2, base_point[1]),
                            WALL_WIDTH,
                        )


    def __checkAdjacentPos(
        self, x: int, y: int, width: int, height: int, checklist: list[tuple[int, int]]
    ):
        # 建立方向列表
        directions = []
        # 这里的坐标(x,y)以单元格为参考系，从0开始,将对应操作数字存入方向列表
        if x > 0:
            if self.isVisited(2 * (x - 1) + 1, 2 * y + 1):
                directions.append(WALL_DIRECTION.WALL_LEFT)
        if y > 0:
            if self.isVisited(2 * x + 1, 2 * (y - 1) + 1):
                directions.append(WALL_DIRECTION.WALL_UP)
        if x < width - 1:
            if self.isVisited(2 * (x + 1) + 1, 2 * y + 1):
                directions.append(WALL_DIRECTION.WALL_RIGHT)
        if y < height - 1:
            if self.isVisited(2 * x + 1, 2 * (y + 1) + 1):
                directions.append(WALL_DIRECTION.WALL_DOWN)
        if len(directions):
            # 随机选择方向
            direction = choice(directions)
            if direction == WALL_DIRECTION.WALL_LEFT:
                self.setMap(2 * (x - 1) + 1, 2 * y + 1, MAP_ENTRY_TYPE.MAP_EMPTY)  # 左侧单元格
                self.setMap(2 * x, 2 * y + 1, MAP_ENTRY_TYPE.MAP_EMPTY)  # 左侧墙壁
                checklist.append((x - 1, y))  # 将左侧单元格坐标添加到检查清单中
            elif direction == WALL_DIRECTION.WALL_UP:
                self.setMap(2 * x + 1, 2 * (y - 1) + 1, MAP_ENTRY_TYPE.MAP_EMPTY)  # 上侧单元格
                self.setMap(2 * x + 1, 2 * y, MAP_ENTRY_TYPE.MAP_EMPTY)  # 上侧墙壁
                checklist.append((x, y - 1))  # 将上侧单元格坐标添加到检查清单中
            elif direction == WALL_DIRECTION.WALL_RIGHT:
                self.setMap(2 * (x + 1) + 1, 2 * y + 1, MAP_ENTRY_TYPE.MAP_EMPTY)  # 右侧单元格
                self.setMap(2 * x + 2, 2 * y + 1, MAP_ENTRY_TYPE.MAP_EMPTY)  # 右侧墙壁
                checklist.append((x + 1, y))  # 将右侧单元格坐标添加到检查清单中
            elif direction == WALL_DIRECTION.WALL_DOWN:
                self.setMap(2 * x + 1, 2 * (y + 1) + 1, MAP_ENTRY_TYPE.MAP_EMPTY)  # 下侧单元格
                self.setMap(2 * x + 1, 2 * y + 2, MAP_ENTRY_TYPE.MAP_EMPTY)  # 下侧墙壁
                checklist.append((x, y + 1))  # 将下侧单元格坐标添加到检查清单中
            return False
        else:
            # 没有找到任何未被访问的元素
            return True

    # Prim算法主函数
    def __randomPrim(self, width: int, height: int):
        # 随机生成起始坐标（以单元格为参考）
        startX, startY = (randint(0, width - 1), randint(0, height - 1))
        # 显示开始的坐标
        # print("start(%d, %d)" % (startX, startY))
        # 初始化起点
        self.setMap(2 * startX + 1, 2 * startY + 1, MAP_ENTRY_TYPE.MAP_EMPTY)
        # 建立检查清单存放有未被访问过的相邻元素的元素坐标
        checklist = []
        checklist.append((startX, startY))  # 将起点作为一个元素放入清单
        while len(checklist):
            # 随机从列表中选取一个元素
            entry = choice(checklist)
            if self.__checkAdjacentPos(entry[0], entry[1], width, height, checklist):
                # 该元素对应的单元格四周已经没有未被访问的相邻单元格，将该元素从检查清单列表中删除
                checklist.remove(entry)

    def __doRandomPrim(self):
        # 将所有map元素先设置为墙壁
        self.resetMap(MAP_ENTRY_TYPE.MAP_BLOCK)
        self.__randomPrim((self.width - 1) // 2, (self.height - 1) // 2)
