from abc import ABC, abstractmethod
from pygame import Surface
from pymunk import Body, Shape, Space


class GameObject(ABC):
    """
    游戏物体抽象基类
    """

    surface: Surface
    """
    物体图像
    """

    body: Body
    """
    物理世界物体
    """

    shapes: list[Shape]
    """
    物理世界复合形状
    """

    def __init__(self, surface: Surface, body: Body, shapes: list[Shape]):
        self.surface = surface
        self.body = body
        self.shapes = shapes

    @abstractmethod
    def draw(self, screen: Surface):
        """
        每帧绘制物体的方法
        """
        pass

    def setBody(self, space: Space):
        """
        设置物体在物理世界的属性的方法
        """
        space.add(self.body, *self.shapes)
