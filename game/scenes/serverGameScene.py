from loguru import logger
from pygame import KEYDOWN, KEYUP, K_a, K_d, K_g, K_s, K_w
from pygame.event import Event
from game.eventManager import EventManager
from game.defines import GAME_ITEM_APPEAR_EVENT_TYPE, ONLINE_KEYDOWN_EVENT_TYPE, ONLINE_KEYUP_EVENT_TYPE, SERVER_SCENE_DATA_EVENT_TYPE
from game.keyPressedManager import ONLINE
from game.operateable import Operation
from game.scenes.localGameScene import LocalGameScene
from online.onlineManager import OnlineManager


class ServerGameScene(LocalGameScene):

    def __init__(self):
        logger.debug("服务器游戏场景初始化")
        super().__init__()
        EventManager.addHandler(
            GAME_ITEM_APPEAR_EVENT_TYPE, lambda e: OnlineManager.sendEvent(e.type, e.dict)
        )

    def generateTanks(self):
        redTank, greenTank = super().generateTanks()
        greenTank.operation = Operation(K_w, K_s, K_a, K_d, K_g, ONLINE)
        return (redTank, greenTank)

    def process(self, event: Event):
        super().process(event)
        if event.type == KEYDOWN:
            OnlineManager.sendEvent(ONLINE_KEYDOWN_EVENT_TYPE, {"key": event.key})
        elif event.type == KEYUP:
            OnlineManager.sendEvent(ONLINE_KEYUP_EVENT_TYPE, {"key": event.key})

    def onEntered(self):
        super().onEntered()
        OnlineManager.sendEvent(
            SERVER_SCENE_DATA_EVENT_TYPE,
            {
                "map": self.gameMap.map,
                "redTank": (
                    self.redTank.body.position,
                    self.redTank.body.angle,
                    self.redTank.operation,
                ),
                "greenTank": (
                    self.greenTank.body.position,
                    self.greenTank.body.angle,
                    self.greenTank.operation,
                ),
            },
        )

    def isGameMenuPauseGame(self) -> bool:
        return False

    def onLeaved(self):
        super().onLeaved()
        OnlineManager.close()
