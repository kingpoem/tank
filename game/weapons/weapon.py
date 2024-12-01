from abc import ABC, abstractmethod

from pygame import Surface

from game.gameObject import GameObject


class Weapon(ABC):
    """
    武器类
    """

    owner: GameObject

    def __init__(self, owner: GameObject):
        self.owner = owner
        pass


    def render(self,screen : Surface):
        """
        在武器可以使用的时候，武器进行附加渲染
        """
        pass

    @abstractmethod
    def fire(self):
        """
        开火方法
        """
        pass

    @abstractmethod
    def canFire(self) -> bool:
        """
        判断是否可以开火
        """
        pass

    @abstractmethod
    def canUse(self) -> bool:
        """
        判断武器是否可以使用
        """
        pass
