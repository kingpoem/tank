from typing import Any
import numpy as np
from pygame import Surface, image, transform, draw
from pymunk import Arbiter, Body, Shape, Space, Poly

from game.bullet import Bullet
from game.bulletManager import bulletsInstance
from game.gameObject import GameObject
from game.gameSpace import GameSpace

TANK_WIDTH = 50
# TANK_HEIGHT = 60


class Tank(GameObject):

    def __init__(self, initX: float, initY: float):
        o_img = image.load("assets/red_tank.png").convert_alpha()
        self.surface = transform.scale_by(
            o_img,
            TANK_WIDTH / o_img.get_width(),
        )
        # self.img.fill((255, 255, 0, 0), special_flags=pygame.BLEND_RGBA_MAX)
        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (initX, initY)
        self.body.moment = 10000
        self.body.mass = 100


        TANK_BODY_RATE = 0.6
        TANK_GUN_RATE = 0.2

        self.shapes = [
            Poly(
                self.body,
                [
                    (-self.surface.get_width() / 2, -self.surface.get_height() / 2),
                    (
                        (self.surface.get_width() / 2) * TANK_BODY_RATE,
                        -self.surface.get_height() / 2,
                    ),
                    (
                        (self.surface.get_width() / 2) * TANK_BODY_RATE,
                        self.surface.get_height() / 2,
                    ),
                    (-self.surface.get_width() / 2, self.surface.get_height() / 2),
                ],
            ),
            Poly(
                self.body,
                [
                    (
                        0,
                        (-self.surface.get_height() / 2) * TANK_GUN_RATE,
                    ),
                    (
                        (self.surface.get_width() / 2),
                        (-self.surface.get_height() / 2) * TANK_GUN_RATE,
                    ),
                    (
                        (self.surface.get_width() / 2),
                        (self.surface.get_height() / 2) * TANK_GUN_RATE,
                    ),
                    (
                        0,
                        (self.surface.get_height() / 2) * TANK_GUN_RATE,
                    ),
                ],
            ),
        ]
        for shape in self.shapes:
            shape.collision_type = GameSpace.TANK_COLLISION_TYPE
            shape.friction = 1

        pass


    def draw(self, screen: Surface):
        # 旋转图片 pymunk和pygame旋转方向相反
        if self.body.space:
            r_img = transform.rotate(self.surface, np.rad2deg(-self.body.angle))
            screen.blit(r_img, r_img.get_rect(center=self.body.position))
        
    def shoot(self):
        if self.body.space:
            bullet = Bullet(
                self.body.position.x + self.body.rotation_vector.x * self.surface.get_width() / 2,
                self.body.position.y + self.body.rotation_vector.y * self.surface.get_width() / 2,
                self.body.angle,
            )
            bulletsInstance.registerBullet(bullet)
        pass


