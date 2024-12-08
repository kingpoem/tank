import pickle
import socket
import threading
from typing import Any, Sequence

from loguru import logger
from pygame import Surface
from pygame.event import Event
from game.eventManager import EventManager
from game.defines import SERVER_SCENE_DATA_EVENT_TYPE
from game.keyPressedManager import LOCAL
from game.sceneManager import SCENE_TYPE, SceneManager
from online.onlineData import EventData
from utils.onlineUtil import recvAll

RE_CONNECT_EVENT_TYPE = EventManager.allocateEventType()
CHECK_CONNECTION_EVENT_TYPE = EventManager.allocateEventType()
CLOSE_CONNECTION_EVENT_TYPE = EventManager.allocateEventType()

MAP_DATA_EVENT_TYPE = EventManager.allocateEventType()
GAMEOBJECT_DATA_EVENT_TYPE = EventManager.allocateEventType()


class OnlineManager:

    class __Server:
        __server: socket.socket
        __client: socket.socket | None = None
        __thread: threading.Thread

        def __init__(self, host: str, port: int):
            self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__server.bind((host, port))
            self.__server.listen(1)

            logger.info(f"服务器已启动 {self.__server.getsockname()}")

            def __serverThread():
                try:
                    self.__client, address = self.__server.accept()
                except Exception as e:
                    logger.exception("服务器接收客户端连接失败", e)
                    EventManager.raiseEventType(CLOSE_CONNECTION_EVENT_TYPE)
                    return
                logger.info(f"客户端已连接：{address}")

                def __checkConnection():
                    try:
                        if self.__client is not None:
                            self.__client.send(pickle.dumps(0))
                    except:
                        logger.info("客户端断开连接")
                        EventManager.raiseEventType(CLOSE_CONNECTION_EVENT_TYPE)
                        SceneManager.changeScene(SCENE_TYPE.START_SCENE)

                EventManager.addHandler(CHECK_CONNECTION_EVENT_TYPE, lambda e: __checkConnection())
                EventManager.setTimer(CHECK_CONNECTION_EVENT_TYPE, 1000)
                SceneManager.changeScene(SCENE_TYPE.SERVER_GAME_SCENE)
                while True:
                    try:
                        bytes = self.__client.recv(2048)
                        logger.debug(f"服务器接收数据 {len(bytes)}")
                        data = pickle.loads(bytes)
                        if isinstance(data, EventData):
                            event: Event
                            if data.data is not None:
                                event = Event(data.eventType, data.data)
                            else:
                                event = Event(data.eventType)
                            EventManager.raiseEvent(event)
                    except ConnectionAbortedError as e:
                        logger.exception("服务器接收数据失败", e)
                    except Exception as e:
                        logger.exception(e)
                        break

            self.__thread = threading.Thread(target=__serverThread)
            self.__thread.start()

            EventManager.addHandler(CLOSE_CONNECTION_EVENT_TYPE, lambda e: self.close())

        def sendEvent(self, eventType: int, data: dict[str, Any]):
            try:
                if self.__client is None:
                    raise Exception("客户端不存在")
                bytes = pickle.dumps(EventData(eventType, data))
                logger.debug(f"服务器发送数据 {len(bytes)}")
                self.__client.send(bytes)
            except Exception as e:
                logger.exception("服务器发送数据失败", e)
                EventManager.raiseEventType(CLOSE_CONNECTION_EVENT_TYPE)
                SceneManager.changeScene(SCENE_TYPE.START_SCENE)

        def close(self):
            EventManager.cancelTimer(CHECK_CONNECTION_EVENT_TYPE)
            EventManager.removeHandler(CHECK_CONNECTION_EVENT_TYPE)
            EventManager.removeHandler(CLOSE_CONNECTION_EVENT_TYPE)
            self.__server.close()
            if self.__client is not None:
                self.__client.close()
                self.__client = None
            self.__thread.join(0)

    class __Client:
        __client: socket.socket
        __thread: threading.Thread

        def __init__(self, host: str, port: int):
            self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            def __clientThread(host: str, port: int):
                try:
                    self.__client.connect((host, port))
                except Exception as e:
                    logger.exception("连接到服务器失败", e)

                def __checkConnection():
                    try:
                        self.__client.send(pickle.dumps(0))
                    except:
                        logger.info("无法连接到服务器")
                        EventManager.raiseEventType(CLOSE_CONNECTION_EVENT_TYPE)
                        SceneManager.changeScene(SCENE_TYPE.START_SCENE)

                EventManager.addHandler(CHECK_CONNECTION_EVENT_TYPE, lambda e: __checkConnection())
                EventManager.setTimer(CHECK_CONNECTION_EVENT_TYPE, 1000)
                EventManager.addHandler(
                    SERVER_SCENE_DATA_EVENT_TYPE,
                    lambda e: SceneManager.changeScene(
                        SCENE_TYPE.CLIENT_GAME_SCENE, True, serverData=e.dict
                    ),
                )

                while True:
                    try:
                        bytes = self.__client.recv(2048)
                        logger.debug(f"客户端接收数据 {len(bytes)}")
                        data = pickle.loads(bytes)
                        if isinstance(data, EventData):
                            event: Event
                            if data.data is not None:
                                event = Event(data.eventType, data.data)
                            else:
                                event = Event(data.eventType)
                            EventManager.raiseEvent(event)
                    except ConnectionAbortedError as e:
                        logger.exception("客户端接收数据失败", e)
                    except Exception as e:
                        logger.exception(e)
                        break

            self.__thread = threading.Thread(target=__clientThread, args=(host, port))
            self.__thread.start()

            EventManager.addHandler(CLOSE_CONNECTION_EVENT_TYPE, lambda e: self.close())

        def sendEvent(self, eventType: int, data: dict[str, Any]):
            try:
                bytes = pickle.dumps(EventData(eventType, data))
                logger.debug(f"发送数据 {len(bytes)}")
                self.__client.send(bytes)
            except Exception as e:
                logger.exception("发送数据失败", e)
                EventManager.raiseEventType(CLOSE_CONNECTION_EVENT_TYPE)
                SceneManager.changeScene(SCENE_TYPE.START_SCENE)

        def close(self):
            EventManager.removeHandler(CHECK_CONNECTION_EVENT_TYPE)
            EventManager.cancelTimer(CHECK_CONNECTION_EVENT_TYPE)
            EventManager.removeHandler(CLOSE_CONNECTION_EVENT_TYPE)
            self.__client.close()
            self.__thread.join(0)

    __onlineObject: __Server | __Client | None = None

    def __init__(self) -> None:
        raise NotImplementedError("OnlineManager不允许实例化")

    @staticmethod
    def createServer(host: str, port: int):
        OnlineManager.close()
        OnlineManager.__onlineObject = OnlineManager.__Server(host, port)

    @staticmethod
    def connectServer(host: str, port: int):
        OnlineManager.close()
        OnlineManager.__onlineObject = OnlineManager.__Client(host, port)

    @staticmethod
    def sendEvent(eventType: int, data: dict[str, Any]):
        if OnlineManager.__onlineObject is None:
            return
        OnlineManager.__onlineObject.sendEvent(eventType, data)

    @staticmethod
    def close():
        if OnlineManager.__onlineObject is None:
            return
        OnlineManager.__onlineObject.close()
        OnlineManager.__onlineObject = None
