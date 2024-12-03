BACKGROUND = (224, 224, 224)
FONT_COLOR = (31, 31, 31)

MENU_BACKGROUND = (192, 192, 192)
MENU_ENV_BACKGROUND = (120, 120, 120, 100)


def getFont(size: float = 32):
    from pygame.freetype import Font

    return Font("C:\\Windows\\Fonts\\msyh.ttc", size)


def easeLinear(time: float, start: float, end: float, duration: float):
    return (end - start) * time / duration + start
