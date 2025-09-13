import math
import random

from heapq import heappop, heappush
from typing import List, Optional, Tuple

from tank.game.bullets.commonBullet import CommonBullet
from tank.game.gameMap import MAP_PLOT_TYPE, GameMap
from tank.game.operateable import Operateable
from tank.game.tank import Tank


class AI:
    """
    AI坦克控制器，包含三种主要算法：
    1. A*寻路算法 - 寻找最优路径
    2. 子弹发射控制 - 限制子弹数量为5发
    3. 躲避算法 - 躲避射来的子弹
    """

    def __init__(self, target: Operateable, gameMap: GameMap):
        self.__target = target
        self.__gameMap = gameMap
        self.__currentPath: List[Tuple[int, int]] = []
        self.__pathIndex = 0
        self.__lastPathUpdate = 0.0
        self.__pathUpdateInterval = 0.5  # 每0.5秒更新一次路径

        # 子弹控制
        self.__maxBullets = 5
        self.__currentBullets = 0
        self.__lastShootTime = 0.0
        self.__shootCooldown = 0.3  # 射击冷却时间

        # 躲避控制
        self.__dodgeDirection = 0  # -1左转, 0直行, 1右转
        self.__dodgeTime = 0.0
        self.__maxDodgeTime = 0.5

        # 目标追踪
        self.__targetTank: Optional[Tank] = None
        self.__lastTargetUpdate = 0.0
        self.__targetUpdateInterval = 0.2  # 每0.2秒更新一次目标

    def update(self, delta: float):
        """
        更新AI行为
        """
        currentTime = self.__lastPathUpdate + delta

        # 更新目标坦克
        self.__updateTarget()

        # 检查是否需要躲避子弹
        if self.__shouldDodge():
            self.__performDodge(delta)
            return

        # 更新路径
        if currentTime >= self.__pathUpdateInterval:
            self.__updatePath()
            self.__lastPathUpdate = 0.0
        else:
            self.__lastPathUpdate = currentTime

        # 执行移动
        self.__performMovement(delta)

        # 执行射击
        self.__performShooting(delta)

    def __updateTarget(self):
        """
        更新目标坦克
        """
        currentTime = self.__lastTargetUpdate + 0.016  # 假设60FPS

        if currentTime >= self.__targetUpdateInterval:
            self.__targetTank = self.__findNearestEnemyTank()
            self.__lastTargetUpdate = 0.0
        else:
            self.__lastTargetUpdate = currentTime

    def __findNearestEnemyTank(self) -> Optional[Tank]:
        """
        寻找最近的敌方坦克
        """
        from tank.game.sceneManager import SceneManager
        from tank.game.scenes.gameScene import GameScene

        currentScene = SceneManager.getCurrentScene()
        if not isinstance(currentScene, GameScene):
            return None

        myTank = self.__target
        if not isinstance(myTank, Tank):
            return None

        nearestTank = None
        minDistance = float("inf")

        for obj in currentScene.gameObjectSpace.objects.values():
            if isinstance(obj, Tank) and obj != myTank and obj.isExist:
                distance = math.sqrt(
                    (obj.body.position.x - myTank.body.position.x) ** 2
                    + (obj.body.position.y - myTank.body.position.y) ** 2
                )
                if distance < minDistance:
                    minDistance = distance
                    nearestTank = obj

        return nearestTank

    def __updatePath(self):
        """
        使用A*算法更新路径
        """
        if not self.__targetTank:
            return

        myTank = self.__target
        if not isinstance(myTank, Tank):
            return

        # 获取当前和目标位置
        startPos = self.__worldToGrid(myTank.body.position)
        targetPos = self.__worldToGrid(self.__targetTank.body.position)

        # 使用A*算法计算路径
        path = self.__astar(startPos, targetPos)
        if path:
            self.__currentPath = path
            self.__pathIndex = 0

    def __worldToGrid(self, worldPos) -> Tuple[int, int]:
        """
        将世界坐标转换为网格坐标
        """
        from tank.game.gameMap import MARGIN_X, MARGIN_Y, PLOT_HEIGHT, PLOT_WIDTH

        gridX = int((worldPos.x - MARGIN_X) // PLOT_WIDTH)
        gridY = int((worldPos.y - MARGIN_Y) // PLOT_HEIGHT)

        # 确保在有效范围内
        gridX = max(0, min(gridX, self.__gameMap.width - 1))
        gridY = max(0, min(gridY, self.__gameMap.height - 1))

        return (gridX, gridY)

    def __gridToWorld(self, gridPos: Tuple[int, int]) -> Tuple[float, float]:
        """
        将网格坐标转换为世界坐标
        """
        from tank.game.gameMap import MARGIN_X, MARGIN_Y, PLOT_HEIGHT, PLOT_WIDTH

        worldX = MARGIN_X + gridPos[0] * PLOT_WIDTH + PLOT_WIDTH / 2
        worldY = MARGIN_Y + gridPos[1] * PLOT_HEIGHT + PLOT_HEIGHT / 2

        return (worldX, worldY)

    def __astar(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        A*寻路算法实现
        """

        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def getNeighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            neighbors = []
            x, y = pos

            # 四个方向的邻居
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < self.__gameMap.width
                    and 0 <= ny < self.__gameMap.height
                    and self.__gameMap.map[nx, ny] == MAP_PLOT_TYPE.MAP_EMPTY
                ):
                    neighbors.append((nx, ny))

            return neighbors

        # A*算法实现
        openSet = [(0, start)]
        cameFrom = {}
        gScore = {start: 0}
        fScore = {start: heuristic(start, goal)}

        while openSet:
            current = heappop(openSet)[1]

            if current == goal:
                # 重构路径
                path = []
                while current in cameFrom:
                    path.append(current)
                    current = cameFrom[current]
                path.append(start)
                return path[::-1]

            for neighbor in getNeighbors(current):
                tentativeGScore = gScore[current] + 1

                if neighbor not in gScore or tentativeGScore < gScore[neighbor]:
                    cameFrom[neighbor] = current
                    gScore[neighbor] = tentativeGScore
                    fScore[neighbor] = tentativeGScore + heuristic(neighbor, goal)
                    heappush(openSet, (fScore[neighbor], neighbor))

        return []

    def __performMovement(self, delta: float):
        """
        执行移动
        """
        if not self.__currentPath or self.__pathIndex >= len(self.__currentPath):
            # 没有路径时随机移动
            if random.random() < 0.1:  # 10%概率转向
                random.choice([self.__target.onLeft, self.__target.onRight])(delta)
            else:
                self.__target.onForward(delta)
            return

        myTank = self.__target
        if not isinstance(myTank, Tank):
            return

        # 获取下一个目标点
        nextGridPos = self.__currentPath[self.__pathIndex]
        nextWorldPos = self.__gridToWorld(nextGridPos)

        # 计算方向
        dx = nextWorldPos[0] - myTank.body.position.x
        dy = nextWorldPos[1] - myTank.body.position.y
        targetAngle = math.atan2(dy, dx)

        # 计算角度差
        angleDiff = targetAngle - myTank.body.angle
        # 标准化角度差到[-π, π]
        while angleDiff > math.pi:
            angleDiff -= 2 * math.pi
        while angleDiff < -math.pi:
            angleDiff += 2 * math.pi

        # 根据角度差决定转向
        if abs(angleDiff) > 0.1:  # 如果角度差大于阈值
            if angleDiff > 0:
                self.__target.onRight(delta)
            else:
                self.__target.onLeft(delta)
        else:
            # 角度接近时前进
            self.__target.onForward(delta)

            # 检查是否到达目标点
            distance = math.sqrt(dx**2 + dy**2)
            if distance < 30:  # 接近目标点时移动到下一个点
                self.__pathIndex += 1

    def __shouldDodge(self) -> bool:
        """
        检查是否需要躲避子弹
        """
        from tank.game.sceneManager import SceneManager
        from tank.game.scenes.gameScene import GameScene

        currentScene = SceneManager.getCurrentScene()
        if not isinstance(currentScene, GameScene):
            return False

        myTank = self.__target
        if not isinstance(myTank, Tank):
            return False

        # 检查附近是否有子弹
        for obj in currentScene.gameObjectSpace.objects.values():
            if isinstance(obj, CommonBullet):
                # 计算子弹到坦克的距离
                dx = obj.body.position.x - myTank.body.position.x
                dy = obj.body.position.y - myTank.body.position.y
                distance = math.sqrt(dx**2 + dy**2)

                # 如果子弹在危险范围内
                if distance < 100:
                    # 计算子弹是否会击中坦克
                    bulletVel = obj.body.velocity
                    if bulletVel.length > 0:
                        # 预测子弹路径
                        timeToHit = distance / bulletVel.length
                        futureBulletPos = (
                            obj.body.position.x + bulletVel.x * timeToHit,
                            obj.body.position.y + bulletVel.y * timeToHit,
                        )

                        # 检查预测位置是否接近坦克当前位置
                        futureDx = futureBulletPos[0] - myTank.body.position.x
                        futureDy = futureBulletPos[1] - myTank.body.position.y
                        futureDistance = math.sqrt(futureDx**2 + futureDy**2)

                        if futureDistance < 50:  # 危险阈值
                            return True

        return False

    def __performDodge(self, delta: float):
        """
        执行躲避动作
        """
        if self.__dodgeTime <= 0:
            # 随机选择躲避方向
            self.__dodgeDirection = random.choice([-1, 1])
            self.__dodgeTime = self.__maxDodgeTime

        # 执行躲避
        if self.__dodgeDirection == -1:
            self.__target.onLeft(delta)
        else:
            self.__target.onRight(delta)

        # 同时后退
        self.__target.onBack(delta)

        self.__dodgeTime -= delta

    def __performShooting(self, delta: float):
        """
        执行射击
        """
        currentTime = self.__lastShootTime + delta

        if (
            currentTime >= self.__shootCooldown
            and self.__currentBullets < self.__maxBullets
            and self.__targetTank
        ):

            myTank = self.__target
            if isinstance(myTank, Tank):
                # 计算到目标的距离和角度
                dx = self.__targetTank.body.position.x - myTank.body.position.x
                dy = self.__targetTank.body.position.y - myTank.body.position.y
                distance = math.sqrt(dx**2 + dy**2)

                # 如果目标在射程内
                if distance < 200:  # 射程限制
                    targetAngle = math.atan2(dy, dx)
                    angleDiff = targetAngle - myTank.body.angle

                    # 标准化角度差
                    while angleDiff > math.pi:
                        angleDiff -= 2 * math.pi
                    while angleDiff < -math.pi:
                        angleDiff += 2 * math.pi

                    # 如果角度差较小，可以射击
                    if abs(angleDiff) < 0.3:  # 约17度
                        myTank.shoot()
                        self.__currentBullets += 1
                        self.__lastShootTime = 0.0
        else:
            self.__lastShootTime = currentTime

        # 更新子弹计数（通过监听子弹消失事件）
        self.__updateBulletCount()

    def __updateBulletCount(self):
        """
        更新当前子弹数量
        """
        from tank.game.sceneManager import SceneManager
        from tank.game.scenes.gameScene import GameScene

        currentScene = SceneManager.getCurrentScene()
        if not isinstance(currentScene, GameScene):
            return

        # 计算当前场景中的子弹数量
        bulletCount = 0
        for obj in currentScene.gameObjectSpace.objects.values():
            if isinstance(obj, CommonBullet):
                bulletCount += 1

        # 更新子弹计数（简单估算）
        self.__currentBullets = min(bulletCount, self.__maxBullets)
