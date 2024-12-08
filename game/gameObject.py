from abc import ABC, abstractmethod
from typing import Callable
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

    Removed : Callable[[],None] | None = None
    """
    当前物体被移除时调用
    """

    def __init__(self, surface: Surface, body: Body, shapes: list[Shape]):
        self.surface = surface
        self.body = body
        self.shapes = shapes

    @abstractmethod
    def render(self, screen: Surface):
        """
        每帧绘制物体
        """
        pass

    def setBody(self, space: Space):
        """
        设置物理世界物体
        """
        space.add(self.body, *self.shapes)

    def removeBody(self,space : Space):
        """
        移除物理世界物体
        """
        space.remove(self.body,*self.shapes)


    def onEntered(self):
        ...

    def onRemoved(self):
        ...