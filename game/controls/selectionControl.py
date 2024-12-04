from typing import Callable

from pygame import (
    K_DOWN,
    K_KP_ENTER,
    K_LEFT,
    K_RETURN,
    K_RIGHT,
    K_UP,
    KEYDOWN,
    Rect,
    Surface,
    transform,
    gfxdraw,
)
from pygame.event import Event
from game.controls.control import Control
from game.gameResources import FONT_COLOR, MEDIAN_FONT, easeLinear


class Selection:

    __captionFunc: Callable[[], str]
    __enterAction: Callable[[], None]
    __leftAction: Callable[[], None] | None
    __rightAction: Callable[[], None] | None

    @property
    def caption(self):
        return self.__captionFunc()

    @property
    def enterAction(self):
        return self.__enterAction

    @property
    def leftAction(self):
        return self.__leftAction

    @property
    def rightAction(self):
        return self.__rightAction

    def __init__(
        self,
        captionResult: Callable[[], str],
        enterAction: Callable[[], None],
        leftAction: Callable[[], None] | None = None,
        rightAction: Callable[[], None] | None = None,
    ):
        self.__captionFunc = captionResult
        self.__enterAction = enterAction
        self.__leftAction = leftAction
        self.__rightAction = rightAction


class SelectionControl(Control):

    __SELECT_SCALE = 1.2
    __SELECTION_HEIGHT = 72
    __SELECTION_SIGN_HEIGHT = 24

    __selectionControlUI: Surface

    __selections: list[Selection] = []
    __selectIndex: int = 0
    __selectionScale: list[float]

    @property
    def ui(self):
        return self.__selectionControlUI

    def __init__(
        self,
        width: float,
        height: float,
        selections: list[Selection],
    ):
        self.__selections = selections
        self.__selectionScale = [1 for _ in range(len(selections))]
        self.__selectionControlUI = Surface((width, height)).convert_alpha()
        self.__selectionControlUI.fill((0, 0, 0, 0))
        self.update(0)

    def process(self, event: Event):
        if event.type == KEYDOWN:
            if event.key == K_RETURN or event.key == K_KP_ENTER:
                if 0 <= self.__selectIndex <= len(self.__selections):
                    self.__selections[self.__selectIndex].enterAction()
            elif event.key == K_LEFT:
                if 0 <= self.__selectIndex <= len(self.__selections):
                    select = self.__selections[self.__selectIndex]
                    if select.leftAction is not None:
                        select.leftAction()
            elif event.key == K_RIGHT:
                if 0 <= self.__selectIndex <= len(self.__selections):
                    select = self.__selections[self.__selectIndex]
                    if select.rightAction is not None:
                        select.rightAction()
            elif event.key == K_UP:
                self.__selectIndex = (self.__selectIndex - 1 + len(self.__selections)) % len(
                    self.__selections
                )
            elif event.key == K_DOWN:
                self.__selectIndex = (self.__selectIndex + 1) % len(self.__selections)

    def update(self, delta: float):

        for i, select in enumerate(self.__selections):
            if self.__selectIndex == i:
                self.__selectionScale[i] = easeLinear(
                    16 * delta, self.__selectionScale[i], 1 + 0.02, 1
                )
            else:
                self.__selectionScale[i] = easeLinear(
                    16 * delta,
                    self.__selectionScale[i],
                    1 / SelectionControl.__SELECT_SCALE - 0.02,
                    1,
                )

            if (
                self.__selectionScale[i] < (1 / SelectionControl.__SELECT_SCALE)
                and not self.__selectIndex == i
            ):
                continue
            # self.__selectionControlUI.fill(
            #     (0, 0, 0, 0),
            #     Rect(
            #         0,
            #         i * SelectionControl.__SELECTION_HEIGHT + 96,
            #         self.__selectionControlUI.get_width(),
            #         SelectionControl.__SELECTION_HEIGHT,
            #     ),
            # )
            text = transform.smoothscale_by(
                MEDIAN_FONT.render(select.caption, FONT_COLOR)[0],
                min(max(self.__selectionScale[i], 1 / SelectionControl.__SELECT_SCALE), 1),
            )

            basePoint = (
                (self.__selectionControlUI.get_width() - text.get_width()) / 2,
                96 + i * SelectionControl.__SELECTION_HEIGHT,
            )
            self.__selectionControlUI.fill(
                (0, 0, 0, 0),
                Rect(
                    0,
                    basePoint[1],
                    self.__selectionControlUI.get_width(),
                    SelectionControl.__SELECTION_HEIGHT,
                ),
            )
            self.__selectionControlUI.blit(text, basePoint)
            if self.__selectIndex == i:
                rightPoint = (basePoint[0] - 16, basePoint[1] + text.get_height() / 2)
                upPoint = (
                    rightPoint[0] - 16,
                    rightPoint[1] - SelectionControl.__SELECTION_SIGN_HEIGHT / 2,
                )
                downPoint = (
                    rightPoint[0] - 16,
                    rightPoint[1] + SelectionControl.__SELECTION_SIGN_HEIGHT / 2,
                )
                gfxdraw.filled_polygon(
                    self.__selectionControlUI, (rightPoint, upPoint, downPoint), FONT_COLOR
                )

    def render(self, screen: Surface): ...


# TODO 实现能滚动的选择控件
