

from loguru import logger
from game.gameItems.gameItem import GameItem
from game.defines import SMALL_FONT
from game.tank import Tank

from pygame import image,transform


class FragmentWeaponGameItem(GameItem):

    def __init__(self, initX: float, initY: float):
        super().__init__(initX, initY)
        o_img =  image.load("assets/bomb_item.png").convert_alpha()
        img = transform.smoothscale(o_img,self.surface.get_size())
        self.surface.blit(img,(0,0))

    @staticmethod
    def onTouched(tank: Tank):
        from game.weapons.fragmentBombWeapon import FragmentBombWeapon
        tank.weapon = FragmentBombWeapon(tank)
        logger.debug(f"当前坦克道具 {tank.weapon}")