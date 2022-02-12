import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import random

## Class definition:


## Fields:

## Interface
class Agent:

	def __init__(self, position, init_velocity, size = 1, energy=5, sight_range=10, max_speed=1, max_acc=1):
		self.pos = position 
		self.vel = init_velocity
		pass
		

	def determine_next_move(self):
		#TODO get this to work with sight range, energy, food locations
		# given the environment/state, figure out what to do next
		ax = np.array([[1]])
		ay = np.array([[0]])
		
		# pack together the acceleration components
		a = np.hstack((ax,ay))

		return a