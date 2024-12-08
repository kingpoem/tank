

from loguru import logger
from game.gameItems.gameItem import GameItem
from game.defines import SMALL_FONT
from game.tank import Tank


class FragmentWeaponGameItem(GameItem):

    def __init__(self, initX: float, initY: float):
        super().__init__(initX, initY)
        SMALL_FONT.render_to(self.surface, (0, 0), "F", (200, 200, 200))

    @staticmethod
    def onTouched(tank: Tank):
        from game.weapons.fragmentBombWeapon import FragmentBombWeapon
        tank.weapon = FragmentBombWeapon(tank)
        logger.debug(f"当前坦克道具 {tank.weapon}")