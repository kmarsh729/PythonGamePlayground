import pygame
import sys
import numpy as np

from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

gameSurface = pygame.display.set_mode((640, 480))
font = pygame.font.Font(None, 32)


##########
# The NN #
##########

class SnakeNN:
    def __init__(self, weights=[]):
        self.num_inputs_nodes = 9
        self.num_hidden_nodes = 12
        self.num_output_nodes = 4
        self.num_weights = self.num_inputs_nodes * self.num_hidden_nodes + self.num_hidden_nodes * self.num_output_nodes

        if len(weights) != 0 and len(weights) != self.num_weights:
            sys.stderr("Weights given to the snake\'s NN aren't the right length.  Brain surgery isn't for you.")
            random_weights = np.random.random(self.num_weights)
            self.weights = np.array(random_weights)
        elif len(weights) == self.num_weights:
            self.weights = np.array(weights)
        else:
            random_weights = self.num_weights
            self.weights = np.array(random_weights)

    def getDirectionToMove(self, direction, head_x, head_y, food_x, food_y, body_distance):
        # Input Node Guide:
        # 0 - distance to wall from front of head
        # 1 - distance to wall from right of head
        # 2 - distance to wall from left of head
        # 3 - distance to body from front of head
        # 4 - distance to body from right of head
        # 5 - distance to body from left of head
        # 6 - distance to food from front of head
        # 7 - distance to food from right of head
        # 8 - distance to food from left of head

        ### Useful Values

        WallPercentX = head_x/40
        WallPercentY = head_y/30
        FoodPercentX = (head_x-food_x)/40
        FoodPercentY = (head_y-food_y)/30

        ###


##########################
# Data Container Classes #
##########################

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class GameData:
    def __init__(self):
        self.lives = 1
        self.isDead = False
        self.blocks = []
        self.tick = 100
        self.speed = 100
        self.level = 1
        self.berrycount = 0  # Number berries eaten
        self.segments = 1  # Segments gained upon eating a berry
        self.frame = 0

        bx = np.random.randint(1, 38)
        by = np.random.randint(1, 28)

        self.berry = Position(bx, by)
        self.blocks.append(Position(20, 15))
        self.blocks.append(Position(19, 15))
        self.direction = 0  # 0 - right, 1 - left, 2 - up, 3 - down


def loseLife(gamedata):
    gamedata.lives -= 1
    gamedata.direction = 0
    gamedata.blocks[:] = []
    gamedata.blocks.append(Position(20, 15))
    gamedata.blocks.append(Position(19, 15))


def positionBerry(gamedata):
    bx = np.random.randint(1, 38)
    by = np.random.randint(1, 28)
    found = True
    while found:
        found = False

        if found:
            bx = np.random.randint(1, 38)
            by = np.random.randint(1, 28)

    gamedata.berry = Position(bx, by)


def loadMapFile(fileName):
    f = open(fileName, 'r')
    content = f.readlines()
    f.close()
    return content


def headHitBody(gamedata):
    head = gamedata.blocks[0]
    for b in gamedata.blocks:
        if (b != head):
            if (b.x == head.x and b.y == head.y):
                return True
    return False


def headHitWall(map, gamedata):
    row = 0
    for line in map:
        col = 0
        for char in line:
            if char == '1':
                if gamedata.blocks[0].x == col and gamedata.blocks[0].y == row:
                    return True
            col += 1
        row += 1
    return False


def drawData(surface, gamedata):
    text = "Berries = {0}, Generation = {1}"
    info = text.format(gamedata.berrycount, 69)
    text = font.render(info, 0, (255, 255, 255))
    textpos = text.get_rect(centerx=surface.get_width() / 2, top=32)
    surface.blit(text, textpos)


def drawGameOver(surface):
    text1 = font.render("Game Over", 1, (255, 255, 255))
    text2 = font.render("Space to play or close the window", 1, (255, 255, 255))
    cx = surface.get_width() / 2
    cy = surface.get_height() / 2
    textpos1 = text1.get_rect(centerx=cx, top=cy - 48)
    textpos2 = text2.get_rect(centerx=cx, top=cy)
    surface.blit(text1, textpos1)
    surface.blit(text2, textpos2)


def drawWalls(surface, img, map):
    row = 0
    # print(len(map))
    # print(len(map[0]))
    for line in map:
        col = 0
        for char in line:
            if char == '1':
                # print('Painting wall @: %d %d' % (row, col))
                imgRect = img.get_rect()
                imgRect.left = col * 16
                imgRect.top = row * 16
                surface.blit(img, imgRect)

            col += 1
        row += 1


def drawSnake(surface, img, gamedata):
    first = True
    for b in gamedata.blocks:
        dest = (b.x * 16, b.y * 16, 16, 16)
        if first:
            first = False
            src = (((gamedata.direction * 2) + gamedata.frame) * 16, 0, 16, 16)
        else:
            src = (8 * 16, 0, 16, 16)
        surface.blit(img, dest, src)


def updateMovement(gamedata):
    head = gamedata.blocks[0]
    if gamedata.tick < 0:
        gamedata.tick += gamedata.speed
        gamedata.frame += 1
        gamedata.frame %= 2
        if gamedata.direction == 0:
            move = (1, 0)
        elif gamedata.direction == 1:
            move = (-1, 0)
        elif gamedata.direction == 2:
            move = (0, -1)
        else:
            move = (0, 1)
        newpos = Position(head.x + move[0], head.y + move[1])
        # first = True
        for b in gamedata.blocks:
            temp = Position(b.x, b.y)
            b.x = newpos.x
            b.y = newpos.y
            newpos = Position(temp.x, temp.y)


def addSegment(gamedata):
    lastIdx = len(gamedata.blocks) - 1
    for i in range(gamedata.segments):
        blockX = gamedata.blocks[lastIdx].x
        blockY = gamedata.blocks[lastIdx].y
        gamedata.blocks.append(Position(blockX, blockY))


def updateGame(gamedata, time):
    gamedata.tick -= time

    updateMovement(gamedata)

    keys = pygame.key.get_pressed()
    if keys[K_RIGHT] and gamedata.direction != 1:
        gamedata.direction = 0
    elif keys[K_LEFT] and gamedata.direction != 0:
        gamedata.direction = 1
    elif keys[K_DOWN] and gamedata.direction != 2:
        gamedata.direction = 3
    elif keys[K_UP] and gamedata.direction != 3:
        gamedata.direction = 2

    head = gamedata.blocks[0]
    if head.x == gamedata.berry.x and head.y == gamedata.berry.y:
        addSegment(gamedata)
        positionBerry(gamedata)
        gamedata.berrycount += 1


def loadImages():
    wall = pygame.image.load('wall.png')
    berry = pygame.image.load('berry.png')
    snake = pygame.image.load('snake.png')
    return {'wall': wall, 'berry': berry, 'snake': snake}


##############################
# Actual Game Execution Code #
##############################

images = loadImages()
images['berry'].set_colorkey((255, 0, 255))  # Purple pixels will be transparent
snakeMap = loadMapFile('map.txt')
data = GameData()
quitGame = False
isPlaying = False

while not quitGame:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if isPlaying:
        x = np.random.randint(1, 38)
        y = np.random.randint(1, 28)

        rect = images['berry'].get_rect()
        rect.left = data.berry.x * 16
        rect.top = data.berry.y * 16

        # Do update stuff here
        updateGame(data, fpsClock.get_time())
        crashed = headHitWall(snakeMap, data) or headHitBody(data)
        if crashed:
            loseLife(data)
            positionBerry(data)

        isPlaying = (data.lives > 0)

    if isPlaying:
        gameSurface.fill((0, 0, 0))

        # Draw stuff here
        drawWalls(gameSurface, images['wall'], snakeMap)
        gameSurface.blit(images['berry'], rect)
        drawSnake(gameSurface, images['snake'], data)
        drawData(gameSurface, data)
    else:
        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            isPlaying = True
            data = None
            data = GameData()
        drawGameOver(gameSurface)

    pygame.display.update()
    fpsClock.tick(30)
