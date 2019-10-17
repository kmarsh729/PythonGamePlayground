import pygame, os, sys
import numpy as np
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()
surface = pygame.display.set_mode((640, 480))
font = pygame.font.Font(None, 32)

class Position:
    def __init__(self,x , y):
        self.x = x
        self.y = y