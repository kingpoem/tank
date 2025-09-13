from .events.eventManager import EventManager

WINDOW_TITLE = "坦克小游戏"

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 1080

FLOATMENU_WIDTH = 1080
FLOATMENU_HEIGHT = 960

from pymunk.shape_filter import ShapeFilter

WALL_FILTER = ShapeFilter(categories=0b0001)
TANK_CORE_FILTER = ShapeFilter(categories=0b0010, mask=0b1011)
TANK_BORDER_FILTER = ShapeFilter(categories=0b0100, mask=0b0101)
BULLET_FILTER = ShapeFilter(categories=0b1000, mask=0b0011)


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

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FONT_DIR = BASE_DIR / "assets/fonts/noto-cjk"

FONT_REGULAR = FONT_DIR / "NotoSerifCJK-Regular.ttc"
FONT_BOLD = FONT_DIR / "NotoSerifCJK-Medium.ttc"
FONT_EXTRA_BOLD = FONT_DIR / "NotoSerifCJK-Bold.ttc"

SMALL_FONT = Font(FONT_REGULAR, 24)
MEDIAN_FONT = Font(FONT_REGULAR, 32)
LARGE_FONT = Font(FONT_BOLD, 48)
TITLE_FONT = Font(FONT_BOLD, 72)
LARGE_TITLE_FONT = Font(FONT_EXTRA_BOLD, 108)

SELECTION_HEIGHT = 72

GAME_ITEM_APPEAR_TIME = 15
