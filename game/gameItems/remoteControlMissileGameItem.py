

from loguru import logger
from game.gameItems.gameItem import GameItem
from pygame.freetype import Font

from game.tank import Tank


class RemoteControlMissileGameItem(GameItem):
    

    def __init__(self, initX: float, initY: float):
        super().__init__(initX, initY)
        font = Font("C:\\Windows\\Fonts\\msyh.ttc", 20)
        font.render_to(self.surface, (0, 0), "R", (200, 200, 200))

    @staticmethod
    def onTouched(tank: Tank):
        from game.weapons.remoteControlMissileWeapon import RemoteControlMissileWeapon
        tank.weapon = RemoteControlMissileWeapon(tank)
        logger.debug(f"当前坦克道具 {tank.weapon}")