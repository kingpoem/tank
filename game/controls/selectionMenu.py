from typing import Callable
from pygame import K_DOWN, K_ESCAPE, K_KP_ENTER, K_RETURN, K_SPACE, K_UP, KEYDOWN, Surface, gfxdraw
from pygame.event import Event
from game.controls.control import Control
from game.gameResources import FONT_COLOR, MENU_BACKGROUND, MENU_ENV_BACKGROUND, easeLinear, getFont


class SelectionMenu(Control):

    __ui: Surface
    __targetUI: Surface
    __envMask : Surface
    __selection: list[tuple[str, Callable[[], None]]] = []
    __selectIndex: int = 0
    __selectDesFontSize: list[float] = []
    __isMenuShow = bool = False
    __menuBottom: float = -10
    __envMaskAlpha : int = 0

    __SELECT_FONT_SIZE = 32
    __COMMON_FONT_SIZE = 24

    __SELECTION_HEIGHT = 72
    __SELECTION_SIGN_HEIGHT = 24

    @property
    def ui(self) -> Surface:
        return self.__ui

    @property
    def isMenuShow(self):
        return self.__isMenuShow

    @property
    def selection(self) -> list[tuple[str, Callable[[], None]]]:
        return self.__selection

    @selection.setter
    def selection(self, s: list[tuple[str, Callable[[], None]]]):
        self.__selection = s
        self.__selectDesFontSize = [SelectionMenu.__COMMON_FONT_SIZE] * len(s)

    def __init__(self, targetUI: Surface, width: float, height: float) -> None:
        self.__ui = Surface((width, height))
        self.__ui.fill(MENU_BACKGROUND)
        self.__targetUI = targetUI
        self.__envMask = Surface(self.__targetUI.get_size()).convert_alpha()
        self.__envMask.fill(MENU_ENV_BACKGROUND)
        


    def process(self, event: Event):
        if event.type == KEYDOWN:
            if event.key == K_RETURN or event.key == K_KP_ENTER:
                if self.__selectIndex in range(len(self.selection)):
                    self.selection[self.__selectIndex][1]()
            elif event.key == K_DOWN:
                self.__selectIndex = (self.__selectIndex + 1) % len(self.selection)
            elif event.key == K_UP:
                self.__selectIndex = (self.__selectIndex - 1 + len(self.selection)) % len(
                    self.selection
                )
            elif event.key == K_ESCAPE:
                self.hide()

    def update(self, delta: float):
        if self.__isMenuShow:
            self.__menuBottom = easeLinear(
                8 * delta,
                self.__menuBottom,
                (self.__targetUI.get_height() + self.__ui.get_height()) / 2,
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

        self.__ui.fill(MENU_BACKGROUND)
        self.__envMask.set_alpha(self.__envMaskAlpha)
        for i, opt in enumerate(self.__selection):
            if self.__selectIndex == i:
                self.__selectDesFontSize[i] = easeLinear(
                    16 * delta, self.__selectDesFontSize[i], SelectionMenu.__SELECT_FONT_SIZE, 1
                )
            else:
                self.__selectDesFontSize[i] = easeLinear(
                    16 * delta, self.__selectDesFontSize[i], SelectionMenu.__COMMON_FONT_SIZE, 1
                )

            o = getFont(self.__selectDesFontSize[i]).render(opt[0], FONT_COLOR)
            basePoint = (
                (self.__ui.get_width() - o[1].width) / 2,
                96 + i * SelectionMenu.__SELECTION_HEIGHT,
            )
            self.__ui.blit(o[0], basePoint)
            if self.__selectIndex == i:
                rightPoint = (basePoint[0] - 16, basePoint[1] + o[1].height / 2)
                upPoint = (
                    rightPoint[0] - 16,
                    rightPoint[1] - SelectionMenu.__SELECTION_SIGN_HEIGHT / 2,
                )
                downPoint = (
                    rightPoint[0] - 16,
                    rightPoint[1] + SelectionMenu.__SELECTION_SIGN_HEIGHT / 2,
                )
                gfxdraw.filled_polygon(self.__ui, (rightPoint, upPoint, downPoint), FONT_COLOR)
        
        self.__targetUI.blit(self.__envMask, (0, 0))
        self.__targetUI.blit(
            self.__ui,
            (
                (self.__targetUI.get_width() - self.__ui.get_width()) / 2,
                self.__menuBottom - self.__ui.get_height(),
            ),
        )

    def render(self, screen: Surface): ...

    def show(self):
        self.__isMenuShow = True

    def hide(self):
        self.__isMenuShow = False
