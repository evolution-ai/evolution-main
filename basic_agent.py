import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygame
import random

## Class definition:


## Fields:

## Interface
class Agent(object):

    def __init__(self, start_x, start_y):

        # state position
        self.current_x = start_x
        self.current_y = start_y

        self.current_velocity = 1
        self.current_direction = 0


    def update_position(self):
        rad_direction = math.radians(self.current_direction)
        self.current_x += self.current_velocity * math.cos(rad_direction)
        self.current_y += self.current_velocity * math.sin(rad_direction)


    def get_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)

    def get_direction(self, x1, y1, x2, y2):
        rad_direction = math.atan(((y1-y2)/(x1-x2)))
        return math.degrees(rad_direction)
    








class Basic_Predator_Agent(Agent):  

    # TODO: add in more agent parameters
    # TODO: make "genetic parameters"
    def __init__(self, start_x: int, start_y: int, preys: list):

        super().__init__(start_x, start_y)

        # # state position
        # self.current_x = start_x
        # self.current_y = start_y

        # # make velocity discrete 1 right now
        # # we need to make this contin
        # self.current_velocity = 1

        # # start with 4 discrete directions
       
        # # right -> 0
        # # up -> 90
        # # left -> 180
        # # down -> 270
        # self.current_direction = 45
        self.preys = preys


    # state is (current_x, current_y, current_velocity, current_direction)

    # number of dimensions in the state
    dim = 4

    # order of the basis functions -> polynomial basis for now
    order = 3

    # total number of such basis
    num_ind = int(pow(order + 1.0, dim))

    # multipliers are the coefficient vectors used within the computation of polynomial function computation
    multipliers = np.zeros((num_ind, dim)) #TODO: not numpy for now

    ## agent hyper parameters
    # exploration vs exploitation
    epsilon_var = 0.03

    # eligibility trace modifier
    lambda_var = 0.5

    # learning rate
    alpha_var = 0.005

    # discount factor
    gamma_var = 0.99

    # temporal difference
    delta_var = 1

    def naive_move(self):

        temp_prey = self.preys[0]

        # TODO: make it pick the closest/ 'best' prey ??

        curr_distance = self.get_distance(self.current_x, self.current_y, temp_prey.current_x, temp_prey.current_y)
        curr_direction = self.get_direction(self.current_x, self.current_y, temp_prey.current_x, temp_prey.current_y)
        
        self.current_direction = curr_direction
        self.update_position()



class Basic_Prey_Agent(Agent):

    # TODO: add in more agent parameters
    # TODO: make "genetic parameters"

    def __init__(self, start_x, start_y, radius):
        
        super().__init__(start_x, start_y)

        # # state position
        # self.current_x = start_x
        # self.current_y = start_y

        # # make velocity discrete 1 right now
        # # we need to make this contin
        # self.current_velocity = 1

        # # start with 4 discrete directions
       
        # # right -> 0
        # # up -> 90
        # # left -> 180
        # # down -> 270
        # self.current_direction = 45

        self.radius = radius

    def random_move(self):

        # TODO: make this move
        self.current_velocity = 2
        self.current_direction = random.randint(0, 359)
        self.update_position()
    
        