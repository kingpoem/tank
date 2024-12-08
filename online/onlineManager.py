import pickle
import socket
import threading
from typing import Any, Sequence

from loguru import logger
from pygame.event import Event
from game.eventManager import EventManager
from game.keyPressedManager import SERVER
from game.sceneManager import SCENE_TYPE, SceneManager
from online.onlineData import EventData


class OnlineManager:

    __server: socket.socket | None = None
    __client: socket.socket | None = None
    __isConnection: bool = False
    __needToClose: bool = False
    __connectThread: threading.Thread | None = None

    def __init__(self) -> None:
        raise NotImplementedError("OnlineManager不允许实例化")

    @staticmethod
    def checkConnection():
        if OnlineManager.__needToClose:
            OnlineManager.close()
            return
        if OnlineManager.__onlineObject is None or OnlineManager.__isConnection is False:
            return

        # if OnlineManager.__isConnection is False:
        #     OnlineManager.close()
        #     return
        try:
            OnlineManager.__onlineObject.sendall(pickle.dumps(0))
        except Exception as e:
            logger.exception("连接断开", e)
            SceneManager.changeScene(SCENE_TYPE.START_SCENE)
            OnlineManager.close()

    @staticmethod
    def createServer(host: str, port: int):
        if OnlineManager.__onlineObject is not None:
            OnlineManager.__onlineObject.close()

        OnlineManager.__onlineObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        OnlineManager.__onlineObject.bind((host, port))
        OnlineManager.__onlineObject.listen(1)
        logger.debug(f"服务端已启动 {OnlineManager.__onlineObject.getsockname()}")

        def __manageClient():
            # 连接客户端
            if OnlineManager.__onlineObject is None:
                return
            try:
                client, addr = OnlineManager.__onlineObject.accept()

                OnlineManager.__isConnection = True
                SceneManager.changeScene(SCENE_TYPE.SERVER_GAME_SCENE)
            except Exception as e:
                logger.exception(e)
                OnlineManager.__needToClose = True
                return
            logger.debug(f"客户端已连接 {addr[0]} {addr[1]}")
            while (bytes := client.recv(512)) and len(bytes) != 0 and OnlineManager.__isConnection:
                try:
                    data = pickle.loads(bytes)
                    if isinstance(data, EventData):
                        event: Event
                        if data.data is not None:
                            event = Event(data.eventType, data.data)
                        else:
                            event = Event(data.eventType)
                        EventManager.raiseEvent(event)
                except Exception as e:
                    logger.exception(e)
                    break

        OnlineManager.__connectThread = threading.Thread(target=__manageClient, args=())
        OnlineManager.__connectThread.start()

    @staticmethod
    def connectServer(host: str, port: int):
        if OnlineManager.__onlineObject is not None:
            OnlineManager.__onlineObject.close()
        OnlineManager.__onlineObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug(f"客户端已启动 {host} {port}")

        def __manageServer():
            while OnlineManager.__isConnection and OnlineManager.__onlineObject is not None:
                try:
                    OnlineManager.__onlineObject.recv(512)
                except Exception as e:
                    logger.exception(e)

        try:
            OnlineManager.__onlineObject.connect((host, port))
            OnlineManager.__connectThread = threading.Thread(target=__manageServer, args=())
            OnlineManager.__connectThread.start()
            logger.success("连接成功")
            OnlineManager.__isConnection = True
            SceneManager.changeScene(SCENE_TYPE.CLIENT_GAME_SCENE)
        except Exception as e:
            logger.exception("连接失败", e)
            SceneManager.changeScene(SCENE_TYPE.START_SCENE)
            OnlineManager.close()

    @staticmethod
    def sendEvent(eventType: int, dict: dict[str, Any]):
        if OnlineManager.__onlineObject is None:
            return
        try:
            bytes = pickle.dumps(EventData(eventType, dict))
            logger.debug(f"发送事件数据 {eventType} {len(bytes)}")
            OnlineManager.__onlineObject.send(bytes)
        except Exception as e:
            logger.exception(e)
            SceneManager.changeScene(SCENE_TYPE.START_SCENE)
            OnlineManager.close()

    # @staticmethod
    # def sendPressed(pressed : tuple[bool,...]):
    #     if OnlineManager.__onlineObject is None:
    #         return
    #     try:
    #         bytes = pickle.dumps(ClientOperation(pressed))
    #         logger.debug(f"发送按键数据 {len(bytes)}")
    #         OnlineManager.__onlineObject.send(bytes)
    #     except Exception as e:
    #         logger.exception(e)
    #         SceneManager.changeScene(SCENE_TYPE.START_SCENE)
    #         OnlineManager.close()

    @staticmethod
    def close():
        OnlineManager.__needToClose = False
        OnlineManager.__isConnection = False
        if OnlineManager.__onlineObject is not None:
            OnlineManager.__onlineObject.close()
            OnlineManager.__onlineObject = None
        if OnlineManager.__connectThread is not None:
            try:
                OnlineManager.__connectThread.join(0.1)
            except Exception as e:
                logger.exception(e)
            OnlineManager.__connectThread = None
