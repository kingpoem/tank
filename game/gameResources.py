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

def easeLinear(time: float, start: float, end: float, duration: float):
    return (end - start) * time / duration + start
