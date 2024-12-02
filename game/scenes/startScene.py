from email.mime import base
from time import sleep
from pygame import K_DOWN, K_KP_ENTER, K_RETURN, K_SPACE, K_UP, KEYDOWN, KSCAN_KP_ENTER, Rect, Surface, gfxdraw
from pygame.freetype import Font
from pygame.event import Event
from pymunk import Space
from game.gameObjectManager import GameObjectManager
from game.resources import BACKGROUND, FONT_COLOR
from game.sceneManager import SCENE_TYPE, SceneManager
from game.scenes.scene import Scene


class StartScene(Scene):

    __ui: Surface

    __selectIndex: int = 0
    __selectRect: list[tuple[float, float]] = []

    __TITLE_HEIGHT = 128

    __SELECT_HEIGHT = 72
    __SELECT_SIGN_MAX_HEIGHT = 24

    __selectSignHeight = __SELECT_SIGN_MAX_HEIGHT

    @property
    def ui(self) -> Surface:
        return self.__ui

    @property
    def gameObjectManager(self) -> GameObjectManager | None:
        return None

    def __init__(self):
        titleFont = Font("C:\\Windows\\Fonts\\msyh.ttc", 72)

        self.__ui = Surface((800, 600))
        self.__ui.fill(BACKGROUND)
        title = titleFont.render("坦 克 动 荡", FONT_COLOR)

        self.__ui.blit(title[0], ((self.ui.get_width() - title[1].width) / 2, 0))

    def process(self, event: Event):
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_RETURN:
                SceneManager.changeScene(SCENE_TYPE.GAME_SCENE)
            elif event.key == K_DOWN:
                self.__selectIndex = (self.__selectIndex + 1) % 2
            elif event.key == K_UP:
                self.__selectIndex = (self.__selectIndex - 1 + 2) % 2

    def update(self, delta: float):
        self.__selectSignHeight = (
            self.__selectSignHeight + StartScene.__SELECT_SIGN_MAX_HEIGHT * delta * 2
        ) % (StartScene.__SELECT_SIGN_MAX_HEIGHT * 2)
        selectFont = Font("C:\\Windows\\Fonts\\msyh.ttc", 32)
        select = [
            selectFont.render("本地游戏", FONT_COLOR),
            selectFont.render("在线游戏", FONT_COLOR),
        ]
        self.__ui.fill(
            BACKGROUND,
            Rect(0, StartScene.__TITLE_HEIGHT, self.__ui.get_width(), self.__ui.get_height()),
        )
        for i, o in enumerate(select):
            basePoint = (
                (self.ui.get_width() - o[1].width) / 2,
                (StartScene.__TITLE_HEIGHT + 48) + i * StartScene.__SELECT_HEIGHT,
            )
            self.__ui.blit(o[0], basePoint)
            if self.__selectIndex == i:
                rightPoint = (basePoint[0] - 16, basePoint[1] + o[1].height / 2)
                upPoint = (
                    rightPoint[0] - 16,
                    rightPoint[1]
                    - abs(StartScene.__SELECT_SIGN_MAX_HEIGHT - 0) / 2,
                )
                downPoint = (
                    rightPoint[0] - 16,
                    rightPoint[1] + abs(StartScene.__SELECT_SIGN_MAX_HEIGHT - 0) / 2,
                )
                gfxdraw.filled_polygon(self.__ui, (rightPoint, upPoint, downPoint), FONT_COLOR)
        pass
