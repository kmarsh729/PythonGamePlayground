import pygame
import sys
import numpy as np
import scipy as sp

from pygame.locals import *
from scipy.special import *

# Setup basic variables needed for the population.
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

pygame.init()
fpsClock = pygame.time.Clock()

gameSurface = pygame.display.set_mode((640, 480))
font = pygame.font.Font(None, 32)
currentGeneration = 1
popSize = 100 # Number of specimens per generation
currentPopulation = -1 # Stupid counting thing requires we start at -1
points_from_berry = sigmoid(0.1*currentGeneration-2) #Number of points we get for eating a berry, increases over time
points_from_moving = 1-sigmoid(0.1*currentGeneration-2) #Number of points we get for avoiding walls, decreases over time


##########
# The NN #
##########


# One line ReLu activation function.
def ReLu(x):
    return np.max(0,x)

# Function to load map and names
def loadFile(fileName):
    f = open(fileName, 'r')
    content = f.readlines()
    f.close()
    return content

# Load names for snakes
names = loadFile('names.txt')
for i in range(len(names)):
    names[i] = names[i].replace('\n', '')


# Function to create new names from old ones
def mutateNames(name1, name2):
    new_name = ''
    for i in range(len(name1)):
        prob = np.random.random()
        if (prob < 0.5):
            new_name += name1[i]
        else:
            new_name += name2[i]
    return new_name


class SnakeNN:
    def __init__(self, weights=[], name = 'satan'):
        self.name = name
        self.num_inputs_nodes = 9
        self.num_hidden_nodes = 12
        self.num_output_nodes = 4
        self.num_weights = self.num_inputs_nodes * self.num_hidden_nodes + self.num_hidden_nodes * self.num_output_nodes
        self.input_nodes = np.array(self.num_inputs_nodes).reshape(-1, 1)
        self.hidden_nodes = np.array(self.num_hidden_nodes).reshape(-1, 1)
        self.output_nodes = np.array(self.num_output_nodes).reshape(-1, 1)

        # Make sure if we're given weights that the user isn't a complete nitwit.
        if len(weights) != 0 and len(weights) != self.num_weights:
            sys.stderr("Weights given to the snake\'s NN aren't the right length.  Brain surgery isn't for you.")
            random_weights = np.random.randn(self.num_weights)
            self.weights = np.array(random_weights)
        elif len(weights) == self.num_weights:
            self.weights = np.array(weights)
        else:
            random_weights = np.random.randn(self.num_weights)
            self.weights = np.array(random_weights)

        # Parse out weights into matrices
        self.input_to_hidden = self.weights[:self.num_inputs_nodes * self.num_hidden_nodes].reshape(
            self.num_hidden_nodes, self.num_inputs_nodes)

        self.hidden_to_output = self.weights[self.num_inputs_nodes * self.num_hidden_nodes:].reshape(
            self.num_output_nodes, self.num_hidden_nodes)

    def fire(self, input_list):
        # Make sure the inputs we're given match how many inputs we expect
        if len(input_list) != self.num_inputs_nodes:
            sys.stderr("Input dimension mismatch.  Can't fire things.")
            return
        self.input_nodes = np.array(input_list).reshape(-1, 1)

        self.hidden_nodes = self.input_to_hidden.dot(self.input_nodes)
        self.hidden_nodes = np.maximum(self.hidden_nodes,0)
        self.output_nodes = self.hidden_to_output.dot(self.hidden_nodes)
        self.output_nodes = sp.special.softmax(self.output_nodes)

    def getBestDirection(self):
        return self.output_nodes.argmax()

    # A long and tedious function to process location data for the snake
    def preprocessInputs(self, direction, head_x, head_y, food_r, food_l, food_u, food_d, body_r, body_l, body_u,
                         body_d):
        # Input Node Guide (All these should be normalized):
        # 0 - distance to wall from front of head
        # 1 - distance to wall from right of head
        # 2 - distance to wall from left of head. Redundant but maybe cool to use if we put obstacles.
        # 3 - distance to body from front of head
        # 4 - distance to body from right of head
        # 5 - distance to body from left of head
        # 6 - distance to food from front of head
        # 7 - distance to food from right of head
        # 8 - distance to food from left of head. Also redundant but maybe add more food?

        if direction == 0:
            return [1 - head_x / 40, 1 - head_y / 30, head_y / 30, body_r / 40, body_d / 30, body_u / 30, food_r / 40,
                    food_d / 30, food_u / 30]

        elif direction == 1:
            return [head_x / 40, head_y / 30, 1 - head_y / 30, body_l / 40, body_u / 30, body_d / 30, food_l / 40,
                    food_u / 30, food_d / 30]

        elif direction == 2:
            return [head_y / 30, 1 - head_x / 40, head_x / 40, body_u / 30, body_r / 40, body_l / 40, food_u / 30,
                    food_r / 40, food_l / 40]

        else:
            return [1 - head_y / 30, head_x / 40, 1 - head_x / 40, body_d / 30, body_l / 40, body_r / 40, food_d / 30,
                    food_l / 40, food_r / 40]

# Allow snakes to initiate coitus, to make sweet sweet love, to get their funk on, do it like they do on Discovery channel
def mateSnakes(snake1,snake2, mutationRate):
    weights1 = snake1.weights
    weights2 = snake2.weights
    new_weights = []

    for i in range(min(len(weights1),len(weights2))):
        if(np.random.rand() < mutationRate):
            new_weights.append(np.random.randn())
        else:
            if(np.random.rand() < 0.5):
                new_weights.append(weights1[i])
            else:
                new_weights.append(weights2[i])

    return SnakeNN(weights = new_weights, name = mutateNames(snake1.name, snake2.name))

##########################
# Data Container Classes #
##########################

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class GameData:
    def __init__(self, snake):
        self.lives = 1
        self.isDead = False
        self.blocks = []
        self.tick = 50#100
        self.speed = 50#100
        self.level = 1
        self.berrycount = 0  # Number berries eaten
        self.segments = 1  # Segments gained upon eating a berry
        self.frame = 0
        self.snakey = snake

        bx = np.random.randint(1, 38)
        by = np.random.randint(1, 28)

        self.berry = Position(bx, by)

        self.direction = np.random.randint(4)  # 0 - right, 1 - left, 2 - up, 3 - down
        if self.direction == 0:
            self.blocks.append(Position(20, 15))
            self.blocks.append(Position(19, 15))
        elif self.direction == 1:
            self.blocks.append(Position(19, 15))
            self.blocks.append(Position(20, 15))
        elif self.direction == 2:
            self.blocks.append(Position(20, 15))
            self.blocks.append(Position(20, 16))
        elif self.direction == 3:
            self.blocks.append(Position(20, 16))
            self.blocks.append(Position(20, 15))


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


def headHitBody(gamedata):
    head = gamedata.blocks[0]
    for b in gamedata.blocks:
        if b != head:
            if b.x == head.x and b.y == head.y:
                return True
    return False


def headFromBodyLeft(gamedata):
    head = gamedata.blocks[0]
    distance = 40
    for b in gamedata.blocks:
        if b != head:
            if b.x < head.x and b.y == head.y:
                distance = min(head.x - b.x, distance)
    return distance


def headFromBodyRight(gamedata):
    head = gamedata.blocks[0]
    distance = 40
    for b in gamedata.blocks:
        if b != head:
            if b.x > head.x and b.y == head.y:
                distance = min(b.x - head.x, distance)
    return distance


def headFromBodyUp(gamedata):
    head = gamedata.blocks[0]
    distance = 30
    for b in gamedata.blocks:
        if b != head:
            if b.x == head.x and b.y < head.y:
                distance = min(head.y - b.y, distance)
    return distance


def headFromBodyDown(gamedata):
    head = gamedata.blocks[0]
    distance = 30
    for b in gamedata.blocks:
        if b != head:
            if b.x == head.x and b.y > head.y:
                distance = min(b.y - head.y, distance)
    return distance


def headFromFoodLeft(gamedata):
    head = gamedata.blocks[0]
    distance = 40
    if gamedata.berry.x < head.x and gamedata.berry.y == head.y:
        distance = min(head.x - gamedata.berry.x, distance)
    return distance


def headFromFoodRight(gamedata):
    head = gamedata.blocks[0]
    distance = 40
    if gamedata.berry.x > head.x and gamedata.berry.y == head.y:
        distance = min(gamedata.berry.x - head.x, distance)
    return distance


def headFromFoodUp(gamedata):
    head = gamedata.blocks[0]
    distance = 30
    if gamedata.berry.x == head.x and gamedata.berry.y < head.y:
        distance = min(head.y - gamedata.berry.y, distance)
    return distance


def headFromFoodDown(gamedata):
    head = gamedata.blocks[0]
    distance = 30
    if gamedata.berry.x == head.x and gamedata.berry.y > head.y:
        distance = min(gamedata.berry.y - head.y, distance)
    return distance


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
    text = "{0}: Score = {1}"
    pygame.display.set_caption(
        'Generation ' + str(currentGeneration) + ' - Current Specimen ' + str(currentPopulation + 1) + '/' + str(
            popSize))
    info = text.format(gamedata.snakey.name, int(gamedata.berrycount))
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
        gamedata.berrycount += points_from_moving
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

    head = gamedata.blocks[0]

    gamedata.snakey.fire(gamedata.snakey.preprocessInputs(gamedata.direction, head.x, head.y, headFromFoodRight(gamedata), headFromFoodLeft(gamedata), headFromBodyUp(gamedata), headFromBodyDown(gamedata), headFromFoodRight(gamedata), headFromBodyLeft(gamedata), headFromBodyUp(gamedata),
                         headFromBodyDown(gamedata)))
    directiondesired = gamedata.snakey.getBestDirection()
    if directiondesired == 0 and gamedata.direction != 1:
        gamedata.direction = 0
    elif directiondesired == 1 and gamedata.direction != 0:
        gamedata.direction = 1
    elif directiondesired == 3 and gamedata.direction != 2:
        gamedata.direction = 3
    elif directiondesired == 2 and gamedata.direction != 3:
        gamedata.direction = 2

    if head.x == gamedata.berry.x and head.y == gamedata.berry.y:
        addSegment(gamedata)
        positionBerry(gamedata)
        gamedata.berrycount += points_from_berry


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
snakeMap = loadFile('map.txt')
# data = GameData()
quitGame = False
isPlaying = False

gds = []
for i in range(popSize):
    gds.append(GameData(SnakeNN(
            name=names[np.random.randint(0, len(names))] + ' ' + names[np.random.randint(0, len(names))])))



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
        isPlaying = True
        data = None
        if currentPopulation == popSize - 1:
            print('reached end of population, resetting')

            points_from_berry = sigmoid(0.1*currentGeneration-2)
            points_from_moving = 1-sigmoid(0.1*currentGeneration-2)

            currentPopulation = 0
            currentGeneration += 1

            maxberries = 0
            strong = []
            # TODO:High berry count should correspond to having a higher chance to be a parent, i.e., size matters.
            # TODO:Maybe make distribution based Prob = specimen_points / sum(specimen_points)
            for g in gds:
                if g.berrycount > maxberries:
                    maxberries = g.berrycount
            print("%.2f"%maxberries)
            for g in gds:
                if g.berrycount >= 0.5*maxberries:
                    strong.append(g)


            if len(strong) < 0.10*popSize:
                print("Only %d worthy specimens, we need to add some more."%len(strong))
                while len(strong) < 0.10*popSize:
                    strong.append(GameData(SnakeNN(
            name=names[np.random.randint(0, len(names))] + ' ' + names[np.random.randint(0, len(names))])))
            else:
                print("%d worthy specimens, now to make tons of snakelets." % len(strong))


            #print(len(strong))
            gds = []

            for i in range(popSize):
                gd1 = np.random.choice(strong)
                gd2 = np.random.choice(strong)
                new_snake = mateSnakes(gd1.snakey, gd2.snakey, 0.01)

                gds.append(GameData(new_snake))
            data = gds[currentPopulation]
            #print(currentPopulation)




        else:
            currentPopulation += 1
            data = gds[currentPopulation]
            #print(currentPopulation)

    pygame.display.update()
    fpsClock.tick(30)
