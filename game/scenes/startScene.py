from email.mime import base
from mimetypes import suffix_map
from time import sleep
from typing import Callable
from loguru import logger
from pygame import (
    K_DOWN,
    K_ESCAPE,
    K_KP_ENTER,
    K_RETURN,
    K_SPACE,
    K_UP,
    KEYDOWN,
    KSCAN_KP_ENTER,
    Rect,
    Surface,
    gfxdraw,
)
import pygame
from pygame.freetype import Font
from pygame.event import Event
from pymunk import Space
from pygame import image, transform
from game.controls.selectionMenu import SelectionMenu
from game.eventManager import EventManager
from game.gameObjectManager import GameObjectManager
from game.gameResources import BACKGROUND, FONT_COLOR, MENU_BACKGROUND, easeLinear, getFont
from game.sceneManager import SCENE_TYPE, SceneManager
from game.scenes.scene import Scene


class StartScene(Scene):

    __ui: Surface
    __background: Surface
    __title: Surface
    # __settingMenu: Surface

    __selectIndex: int = 0
    __selections: list[tuple[str, Callable[[], None]]]
    __selectionDesFontSize: dict[str, float] = {}

    __settingMenu: SelectionMenu
    __settingMenuSelections: list[tuple[str, Callable[[], None]]]


    __SELECT_HEIGHT = 72
    __SELECT_SIGN_HEIGHT = 24

    @property
    def ui(self) -> Surface:
        return self.__ui

    @property
    def gameObjectManager(self) -> GameObjectManager | None:
        return None

    def __init__(self):

        self.__selections = [
            ("本地游戏", self.__onLocalGameEnter),
            ("在线游戏", self.__onOnlineGameEnter),
            ("设置", self.__onSettingEnter),
            ("退出游戏", self.__onExitGameEnter),
        ]
        self.__settingMenuSelections = [
            ("音量", lambda: None),
            ("音效", lambda: None),
            # ("返回", lambda: None),
        ]

        self.__ui = Surface((1440, 1280))
        img = image.load("assets/background.png").convert_alpha()
        self.__background = transform.smoothscale_by(
            img, (self.__ui.get_width() + 108) / img.get_width()
        )
        self.__title = getFont(72).render("坦 克 动 荡", FONT_COLOR)[0]
        self.__settingMenu = SelectionMenu(self.__ui, 1280, 960)
        self.__settingMenu.selection = self.__settingMenuSelections
        # self.__settingMenu = pygame.Surface((1280, 960))
        # self.__settingMenu.fill(MENU_BACKGROUND)

        logger.debug("主菜单场景初始化完成")

    def process(self, event: Event):
        if self.__settingMenu.isMenuShow:
            self.__settingMenu.process(event)
            return

        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_RETURN:
                self.__selections[self.__selectIndex][1]()

            elif event.key == K_DOWN:

                self.__selectIndex = (self.__selectIndex + 1) % len(self.__selections)
            elif event.key == K_UP:

                self.__selectIndex = (self.__selectIndex - 1 + len(self.__selections)) % len(
                    self.__selections
                )

    def update(self, delta: float):
        self.__ui.fill(BACKGROUND)
        self.__ui.blit(
            self.__background, self.__background.get_rect(center=self.__ui.get_rect().center)
        )

        self.__ui.blit(self.__title, ((self.ui.get_width() - self.__title.get_width()) / 2, 48))
        self.__updateSelection(delta)
        self.__updateSettingMenu(delta)

    def __updateSelection(self, delta: float):
        SELECT_FONT_SIZE = 32
        COMMON_FONT_SIZE = 24

        for i, opt in enumerate(self.__selections):
            if opt[0] in self.__selectionDesFontSize:
                if self.__selectIndex == i:
                    self.__selectionDesFontSize[opt[0]] = easeLinear(
                        16 * delta, self.__selectionDesFontSize[opt[0]], SELECT_FONT_SIZE, 1
                    )
                else:
                    self.__selectionDesFontSize[opt[0]] = easeLinear(
                        16 * delta, self.__selectionDesFontSize[opt[0]], COMMON_FONT_SIZE, 1
                    )
            else:
                self.__selectionDesFontSize[opt[0]] = COMMON_FONT_SIZE

            o = getFont(self.__selectionDesFontSize[opt[0]]).render(opt[0], FONT_COLOR)
            basePoint = (
                (self.ui.get_width() - o[1].width) / 2,
                (self.__title.get_height() + 96) + i * StartScene.__SELECT_HEIGHT,
            )
            self.__ui.blit(o[0], basePoint)
            if self.__selectIndex == i:
                rightPoint = (basePoint[0] - 16, basePoint[1] + o[1].height / 2)
                upPoint = (
                    rightPoint[0] - 16,
                    rightPoint[1] - StartScene.__SELECT_SIGN_HEIGHT / 2,
                )
                downPoint = (
                    rightPoint[0] - 16,
                    rightPoint[1] + StartScene.__SELECT_SIGN_HEIGHT / 2,
                )
                gfxdraw.filled_polygon(self.__ui, (rightPoint, upPoint, downPoint), FONT_COLOR)

    def __updateSettingMenu(self, delta: float):
        self.__settingMenu.update(delta)

    def __onLocalGameEnter(self):
        SceneManager.changeScene(SCENE_TYPE.GAME_SCENE)

    def __onOnlineGameEnter(self): ...

    def __onSettingEnter(self):
        self.__settingMenu.show()

    def __onExitGameEnter(self):
        EventManager.raiseEvent(pygame.QUIT)
