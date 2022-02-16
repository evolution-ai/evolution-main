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
	sight_range = 20.0, max_speed = 5.0, max_acc = 5.0, eat_range = 1.0):
		self.pos = position 
		self.vel = init_velocity

		self.energy = energy
		self.sight_range = sight_range
		self.max_speed = max_speed
		self.max_acc = max_acc
		self.eat_range = eat_range
		pass
		

	def determine_next_move(self, food_dict):
		#TODO get this to work with sight range, energy, food locations
		# given the environment/state, figure out what to do next

		#TODO: I'm going to write basic functionality first, we need to speed up with vectorisation
		
		dists = []

		# find distance to each food within sight
		for food_loc in food_dict:

			delta_x = food_loc[0] - self.pos[0]
			delta_y = food_loc[1] - self.pos[1]
			euclidean = math.sqrt(delta_x**2 + delta_y**2)

			if euclidean < self.sight_range:
				dists.append((euclidean, food_loc))
		
		dists.sort()

		to_eat_action = (False, (0,0))

		if len(dists) > 0:
			(min_dist, food_loc) = dists[0]
			closest_food = (food_loc[0] - self.pos[0], food_loc[1] - self.pos[1])
			
			if min_dist < self.eat_range:
				to_eat_action = (True, food_loc)

		else:
			ax = np.random.random((1,))
			ay = np.random.random((1,))
			return (np.hstack((ax,ay)), to_eat_action)

		a = (2 * np.array(closest_food) - self.vel)
		a = (a / np.linalg.norm(a)) * self.max_acc

		# ax = np.array([[1]])
		# ay = np.array([[0]])
		
		# # pack together the acceleration components
		# a = np.hstack((ax,ay))

		self.energy -= 0.1

		return (a, to_eat_action)