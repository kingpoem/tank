from typing import Callable
from pygame import (
    K_DOWN,
    K_ESCAPE,
    K_KP_ENTER,
    K_LEFT,
    K_RETURN,
    K_RIGHT,
    K_SPACE,
    K_UP,
    KEYDOWN,
    Surface,
    gfxdraw,
)
from pygame import transform
from pygame.event import Event
from game.controls.control import Control
from game.controls.selectionControl import Selection, SelectionControl
from game.gameResources import (
    BACKGROUND,
    FONT_COLOR,
    LARGE_FONT,
    MEDIAN_FONT,
    MENU_BACKGROUND,
    MENU_ENV_BACKGROUND,
    easeLinear,
)


class SelectionMenu(SelectionControl):

    __SelectionMenuUI: Surface
    __targetUI: Surface
    __envMask: Surface

    __isMenuShow: bool = False
    __menuBottom: float = -10
    __envMaskAlpha: int = 0

    @property
    def ui(self) -> Surface:
        return self.__SelectionMenuUI

    @property
    def isMenuShow(self):
        return self.__isMenuShow

    def __init__(
        self, targetUI: Surface, width: float, height: float, selections: list[Selection]
    ) -> None:
        super().__init__(width, height, selections)
        self.__SelectionMenuUI = Surface((width, height))
        self.__targetUI = targetUI
        self.__envMask = Surface(self.__targetUI.get_size()).convert_alpha()
        self.__envMask.fill(MENU_ENV_BACKGROUND)

    def process(self, event: Event):
        super().process(event)
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.hide()

    def update(self, delta: float):
        if self.__isMenuShow:
            self.__menuBottom = easeLinear(
                8 * delta,
                self.__menuBottom,
                (self.__targetUI.get_height() + self.ui.get_height()) / 2,
                1,
            )
            self.__envMaskAlpha = int(easeLinear(8 * delta, self.__envMaskAlpha, 255, 1))
        else:
            self.__menuBottom = easeLinear(
                8 * delta,
                self.__menuBottom,
                -10,
                1,
            )
            self.__envMaskAlpha = int(easeLinear(8 * delta, self.__envMaskAlpha, 0, 1))

        if self.__menuBottom <= 0:
            return

        self.ui.fill(MENU_BACKGROUND)
        super().update(delta)
        self.__envMask.set_alpha(self.__envMaskAlpha)

        self.__targetUI.blit(self.__envMask, (0, 0))
        self.ui.blit(
            super().ui,
            (
                (self.ui.get_width() - super().ui.get_width()) / 2,
                (self.ui.get_height() - super().ui.get_height()) / 2,
            ),
        )
        self.__targetUI.blit(
            self.ui,
            (
                (self.__targetUI.get_width() - self.ui.get_width()) / 2,
                self.__menuBottom - self.ui.get_height(),
            ),
        )

    def render(self, screen: Surface): ...

    def needUpdate(self):
        return True

    def show(self):
        self.__isMenuShow = True

    def hide(self):
        self.__isMenuShow = False
