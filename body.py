import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import random

from sklearn.metrics import euclidean_distances

## Class definition:


## Fields:

## Interface
class Agent:

	def __init__(self, position, init_velocity, size = 1.0, energy = 20.0, 
	sight_range = 25.0, max_speed = 5.0, max_acc = 1.0):
		self.pos = position 
		self.vel = init_velocity

		self.energy = energy
		self.sight_range = sight_range
		self.max_speed = max_speed
		self.max_acc = max_acc
		pass
		

	def determine_next_move(self, food_pos):
		#TODO get this to work with sight range, energy, food locations
		# given the environment/state, figure out what to do next

		#TODO: I'm going to write basic functionality first, we need to speed up with vectorisation
		food_pos = food_pos - self.pos
		
		dists = []

		# find distance to each food within sight
		for f in range(food_pos.shape[0]):

			euclidean = math.sqrt(food_pos[f, 0]**2 + food_pos[f, 1]**2)

			if euclidean < self.sight_range:
				dists.append((euclidean, f))

		dists.sort()

		if len(dists) > 0:
			closest_ind = dists[0][1]
		else:
			ax = np.random.random((1,))
			ay = np.random.random((1,))
			return np.hstack((ax,ay))



		a = 2*(food_pos[closest_ind] - self.vel)

		# ax = np.array([[1]])
		# ay = np.array([[0]])
		
		# # pack together the acceleration components
		# a = np.hstack((ax,ay))


		return a