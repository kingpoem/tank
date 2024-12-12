

from loguru import logger
from game.gameItems.gameItem import GameItem
from pygame.freetype import Font
from pygame import image,transform

from game.tank import Tank


class RemoteControlMissileGameItem(GameItem):
    

    def __init__(self, initX: float, initY: float):
        super().__init__(initX, initY)
        o_img =  image.load("assets/missile_item.png").convert_alpha()
        img = transform.smoothscale(o_img,self.surface.get_size())
        self.surface.blit(img,(0,0))

    @staticmethod
    def onTouched(tank: Tank):
        from game.weapons.remoteControlMissileWeapon import RemoteControlMissileWeapon
        tank.weapon = RemoteControlMissileWeapon(tank)
        logger.debug(f"当前坦克道具 {tank.weapon}")