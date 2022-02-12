import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygame
import random

## Class definition:


## Fields:

## Interface
class Agent:

    def __init__(self, game ):
        self.curr_game = game
        # take in game that we want to play
        # 
        pass
        

    def determine_next_move(self):
        # given the environment/state, figure out what to do next
        pass


    def get_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)

    def get_direction(self, x1, y1, x2, y2):
        rad_direction = math.atan(((y1-y2)/(x1-x2)))
        return math.degrees(rad_direction)