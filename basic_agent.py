import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygame

## Class definition:


## Fields:


class Basic_Agent:

    # TODO: add in more agent parameters
    # TODO: make "genetic parameters"
    def __init__(self, start_x, start_y):

        self.start_x = start_x
        self.start_y = start_y

        # state position
        self.current_x = start_x
        self.current_y = start_y

        # make velocity discrete 1 right now
        # we need to make this contin
        self.current_velocity = 1

        # start with 4 discrete directions
       
        # right -> 0
        # up -> 90
        # left -> 180
        # down -> 270
        self.current_direction = 45


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
        self.update_position()
        

    def update_position(self):
        rad_direction = math.radians(self.current_direction)
        self.current_x += self.current_velocity * math.cos(rad_direction)
        self.current_y += self.current_velocity * math.sin(rad_direction)
