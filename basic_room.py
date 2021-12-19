import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygame

## Class definition:
# This class describes the representation and state of the room in which the
# agents will be located

## Fields:
# - Goal: store the x, y coordinates of the goal location in the room
# - x_length: the x dimension of the room 
# - y_length: the y dimension of the room 
# - radius: the radius within which the goal can be reached
# Methods:
# - is_valid_location (x, y,) -> bool: 
#                      checks to see whether a provided set of coordinates is
#                      a valid location in the maze
# - is_goal (x, y) -> bool: checks to see if the agent is at the goal position within some 
#            radius set by the field

class Room:
    def __init__(self, x, y, rad) -> None:
        self.x_length = x
        self.y_length = y
        self.radius = rad
        self.x_goal = x/2 
        self.y_goal = y/2
    
    def is_valid_location(self, x_targ, y_targ):
        return 0 <= x_targ <= self.x_length and 0 <= y_targ <= self.y_length

    def is_goal(self, x_pos, y_pos):
        return (self.x_goal-self.radius <= x_pos <= self.x_goal +self.radius) and (self.y_goal-self.radius <= y_pos <= self.y_goal + self.radius)
