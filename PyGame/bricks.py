import pygame, os, sys
import numpy as np
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()
mainSurface = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Bricks')

black = pygame.Color(0, 0, 0)

def createBricks(pathToImg, rows = 5, cols = 10):
    global brick
    brick = pygame.image.load(pathToImg)
    bricks = []
    for y in range(rows):
        brickY = (y * 24) + 100
        for x in range(cols):
            brickX = (x * 31) + 245
            width = brick.get_width()
            height = brick.get_height()
            rect = Rect(brickX, brickY, width, height)
            bricks.append(rect)
    return bricks


# Init platform
platform = pygame.image.load('platform.png')
playerY = 540
platformRect = platform.get_rect()
mousex, mousey = (0, playerY)

# Init ball
ball = pygame.image.load('ball.png')
ballRect = ball.get_rect()
ballStartY = np.random.randint(300, 450)
ballStartX = np.random.randint(0,800)

ballServed = False
bx, by = (ballStartX, ballStartY)

ballSpeed = 5
angle = np.random.randint(0,180)
sx, sy = (ballSpeed*np.cos(np.deg2rad(angle)), ballSpeed*np.sin(np.deg2rad(angle)))
ballRect.topleft = (bx, by)

# Init brick
bricks = createBricks('brick.png')

while True:
    mainSurface.fill(black)
    # Draw brick
    for b in bricks:
        mainSurface.blit(brick, b)

    # Draw platform and ball
    mainSurface.blit(platform, platformRect)
    mainSurface.blit(ball, ballRect)

    # Events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEMOTION:
            mousex, mousey = event.pos
            if mousex < 800 - 55:
                platformRect.topleft = (mousex, playerY)
            else:
                platformRect.topleft = (800 - 55, playerY)

    # Main game logic
    if ballServed:
        bx += sx
        by += sy
        ballRect.topleft = (bx, by)
    elif event.type == MOUSEBUTTONUP and not ballServed:
        ballServed = True

    if by <= 0:
        by = 0
        sy *= -1
    if by >= 600 - 8:
        ballServed = False
        ballStartY = np.random.randint(300, 450)
        ballStartX = np.random.randint(0, 800)
        bx, by = (ballStartX, ballStartY)

        angle = np.random.randint(0,180)
        ballSpeed = 5
        sx, sy = (ballSpeed*np.cos(np.deg2rad(angle)), ballSpeed*np.sin(np.deg2rad(angle)))
        ballRect.topleft = (bx, by)

    if bx <= 0:
        bx = 0
        sx *= -1
    if bx >= 800 - 8:
        bx = 800 - 8
        sx *= -1

    # Collision detection

    if ballRect.colliderect(platformRect):
        by = playerY - 8
        sy *= -1

    brickHitIndex = ballRect.collidelist(bricks)
    if brickHitIndex >= 0:
        hb = bricks[brickHitIndex]
        mx = bx + 4
        my = by + 4
        if mx > hb.x + hb.width or mx < hb.x:
            sx *= -1.1
        else:
            sy *= -1.1
        del(bricks[brickHitIndex])

    pygame.display.update()
    fpsClock.tick(30)
