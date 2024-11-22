
from game.gameSpace import GameSpace
from game.bullet import Bullet

# TODO BulletManager不合理

class BulletManager:
    bullets : list[Bullet] = []

    def registerBullet(self,bullet: Bullet):
        self.bullets.append(bullet)
        bullet.setBody(GameSpace.getSpace())

    def drawBullets(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)
    
    

bulletsInstance : BulletManager = BulletManager()