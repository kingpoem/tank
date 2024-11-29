from game.gameItems.gameItem import GameItem
from pygame.freetype import Font

from game.tank import Tank
from game.weapons.ghostWeapon import GhostWeapon


class GhostWeaponGameItem(GameItem):

    def __init__(self, initX: float, initY: float):
        super().__init__(initX, initY)
        font = Font("C:\\Windows\\Fonts\\msyh.ttc", 20)
        font.render_to(self.surface, (0, 0), "G", (200, 200, 200))

    @staticmethod
    def onTouched(tank: Tank):
        tank.weapon = GhostWeapon(tank)
        