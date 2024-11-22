from pygame import K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP, key
from game.tank import Tank



class Player:
    tank : Tank

    def __init__(self, tank: Tank):
        self.tank = tank
        pass

    def move(self,delta : float):
        pressed = key.get_pressed()
        # dSpeed = 0
        dAngle = 0
        dPower = 0
        # b.velocity = b.velocity * 0.9
        # b.angular_velocity = b.angular_velocity * 0.9
        if pressed[K_LEFT]:
            dAngle -= 100
        if pressed[K_RIGHT]:
            dAngle += 100
        self.tank.body.angular_velocity = dAngle * delta
        if pressed[K_UP]:
            dPower += 300000
        if pressed[K_DOWN]:
            dPower -= 300000

        if dPower != 0:
            self.tank.body.apply_force_at_world_point(self.tank.body.rotation_vector * dPower * delta * self.tank.body.mass,self.tank.body.position)
        pass
