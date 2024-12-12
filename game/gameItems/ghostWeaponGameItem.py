from loguru import logger
from game.gameItems.gameItem import GameItem
from pygame.freetype import Font
from pygame import image,transform

from game.defines import SMALL_FONT
from game.tank import Tank


class GhostWeaponGameItem(GameItem):

    def __init__(self, initX: float, initY: float):
        super().__init__(initX, initY)
        o_img =  image.load("assets/ghost_item.png").convert_alpha()
        img = transform.smoothscale(o_img,self.surface.get_size())
        self.surface.blit(img,(0,0))
        # SMALL_FONT.render_to(self.surface, (0, 0), "G", (200, 200, 200))

    @staticmethod
    def onTouched(tank: Tank):
        from game.weapons.ghostWeapon import GhostWeapon
        tank.weapon = GhostWeapon(tank)
        logger.debug(f"当前坦克道具 {tank.weapon}")
        