import pygame, os, sys
import numpy as np
from pygame.locals import *


class Ball:
    def __init__(self, x, y, speed, imgPath):
        self.x = x
        self.y = y
        self.speed = speed
        self.img = pygame.image.load(imgPath)
        pass

    # y = np.random.randint(300, 450)
    # x = np.random.randint(0, 800)
    # ballSpeed = 5
    # angle = np.random.randint(0, 180)
    # speed = [ballSpeed * np.cos(np.deg2rad(angle)), ballSpeed * np.sin(np.deg2rad(angle))]
    # img = pygame.image.load('ball.png')

    def update(self, gameTime):
        self.x += self.speed[0]
        self.y += self.speed[1]

        if self.y <= 0:
            self.y = 0
            self.speed[1] = self.speed[1] *  -1
        if self.y >= 600 - 8:
            self.y = 600-8
            self.speed[1] = self.speed[1] *  -1

        if self.x <= 0:
            self.x = 0
            self.speed[0] = self.speed[0] *  -1
        if self.x >= 800 - 8:
            self.x = 800 - 8
            self.speed[0] = self.speed[0] *  -1
        pass

    def hasHitBrick(self, bricks):
        return False

    def hasHitPlatform(self, platform):
        return False

    def draw(self, gameTime, surface):
        surface.blit(self.img, (self.x, self.y))


if __name__ == '__main__':
    pygame.init()
    fpsClock = pygame.time.Clock()
    surface = pygame.display.set_mode((800, 600))
    ballSpeed = 5
    angle = np.random.randint(0, 180)
    ball = Ball(np.random.randint(0, 800), np.random.randint(300, 450), [ballSpeed * np.cos(np.deg2rad(angle)), ballSpeed * np.sin(np.deg2rad(angle))], 'ball.png')
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        ball.update(fpsClock)
        surface.fill((0, 0, 0))
        ball.draw(fpsClock, surface)
        pygame.display.update()
        fpsClock.tick(30)
