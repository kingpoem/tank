
import sys
from loguru import logger
from game.gameLoop import GameLoop
import cProfile
import pstats
# import game.gameResources


def __configureLogger():
    logger.remove(0)
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green>| {file} {line} | <level>{level}</level> | {message}",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    # logger.trace("程序启动")
    # logger.debug("程序启动")
    # logger.info("程序启动")
    # logger.success("程序启动")
    # logger.warning("程序启动")
    # logger.error("程序启动")
    # logger.critical("程序启动")


if __name__ == "__main__":
    # 初始化 logger 配置
    __configureLogger()

    # 开始游戏循环
    GameLoop.run()
    # cProfile.run('GameLoop.run()','states.prof')

    # p = pstats.Stats('states.prof')
    # p.sort_stats(pstats.SortKey.TIME).print_stats('update',20)
    



