from typing import Tuple
from pygame import Surface, draw
from pymunk import Body, Circle, Shape, Space

from game.gameObject import GameObject
from game.gameSpace import GameSpace




class Bullet(GameObject):


    def __init__(self, initX: float, initY: float, initAngle: float):
        def _vec_func(body: Body,gravity : Tuple[float,float], damping : float, dt: float):
            body.update_velocity(body, (0, 0), 1, dt)
            pass

        self.body = Body(body_type=Body.DYNAMIC)
        self.body.position = (initX, initY)
        self.body.angle = initAngle
        self.body.moment = 100
        self.body.mass = 1
        
        # self.body.velocity = (0,0)
        self.body.velocity = self.body.rotation_vector * 300
        self.body.velocity_func = _vec_func

        self.shapes = [Circle(self.body, 4)]
        self.shapes[0].collision_type = GameSpace.BULLET_COLLISION_TYPE
        self.shapes[0].elasticity = 1
        pass

    def draw(self, screen: Surface):
        if self.body.space:
            draw.circle(screen, (0, 0, 0), self.body.position, 4)
        pass


