from abc import ABC, abstractmethod
from loguru import logger
from pygame import Surface
from pymunk import Arbiter, Body, CollisionHandler, Poly, ShapeFilter, Space
from game.gameObject import GameObject
from game.sceneManager import SceneManager
from game.tank import TANK_COLLISION_TYPE, Tank
from typing import Any

GAMEITEM_COLLISION_TYPE = 3


class GameItem(GameObject, ABC):
    """
    游戏道具类
    """

    __collisionHandler: CollisionHandler

    def __init__(self, initX: float, initY: float):
        self.surface = Surface((30, 30))
        self.surface.fill((130, 130, 130))

        self.body = Body(body_type=Body.KINEMATIC)
        self.body.position = (initX, initY)

        self.shapes = [Poly.create_box(self.body, self.surface.get_size())]
        for shape in self.shapes:
            shape.sensor = True
            shape.collision_type = GAMEITEM_COLLISION_TYPE
            # shape.filter = ShapeFilter(categories=0b0001)

    def render(self, screen: Surface):
        screen.blit(self.surface, self.surface.get_rect(center=self.body.position))

    def setBody(self, space: Space):
        super().setBody(space)
        self.__collisionHandler = space.add_collision_handler(
            GAMEITEM_COLLISION_TYPE, TANK_COLLISION_TYPE
        )
        self.__collisionHandler.begin = GameItem.__onTankTouched

    @staticmethod
    def __onTankTouched(arbiter: Arbiter, space: Space, data: dict[Any, Any]):
        item = SceneManager.getCurrentScene().gameObjectManager.getGameObjectByBody(
            arbiter.shapes[0].body
        )
        tank = SceneManager.getCurrentScene().gameObjectManager.getGameObjectByBody(
            arbiter.shapes[1].body
        )
        if isinstance(item, GameItem) and isinstance(tank, Tank):
            item.onTouched(tank)
            SceneManager.getCurrentScene().gameObjectManager.removeObject(item)
        logger.debug(f"道具被坦克碰撞 {item} {tank}")
        return True

    @staticmethod
    @abstractmethod
    def onTouched(tank: Tank):
        pass
