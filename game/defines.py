
from enum import Enum


from .events.eventManager import EventManager

WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 1280

FLOATMENU_WIDTH = 1280
FLOATMENU_HEIGHT = 960

GENERATE_GAME_ITEM_EVENT_TYPE = EventManager.allocateEventType()
"""生成游戏物体事件"""

START_GENERATE_GAME_ITEM_EVENT_TYPE = EventManager.allocateEventType()
GAME_ITEM_APPEAR_EVENT_TYPE = EventManager.allocateEventType()

ONLINE_KEYDOWN_EVENT_TYPE = EventManager.allocateEventType()
ONLINE_KEYUP_EVENT_TYPE = EventManager.allocateEventType()

SERVER_SCENE_DATA_EVENT_TYPE = EventManager.allocateEventType()
# SERVER_GAME_ITEM_EVENT_TYPE = EventManager.allocateEventType()

CLIENT_REQUEST_EVENT_TYPE = EventManager.allocateEventType()

from pygame.freetype import Font

BACKGROUND = (224, 224, 224)
FONT_COLOR = (31, 31, 31)

MENU_BACKGROUND = (192, 192, 192)
MENU_ENV_BACKGROUND = (120, 120, 120, 100)


FONT_FAMILY = "C:\\Windows\\Fonts\\msyh.ttc"
SMALL_FONT = Font(FONT_FAMILY,24)
MEDIAN_FONT = Font(FONT_FAMILY, 32)
LARGE_FONT = Font(FONT_FAMILY, 48)
TITLE_FONT = Font(FONT_FAMILY, 72)
LARGE_TITLE_FONT = Font(FONT_FAMILY, 108)

SELECTION_HEIGHT = 72

GAME_ITEM_APPEAR_TIME = 15


