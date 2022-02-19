import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import random

from sklearn.metrics import euclidean_distances
from dataclasses import dataclass




# @dataclass
# class Action:
# 	accelaration: np.array()
# 	to_eat_action: bool
# 	to_eat_loc: tuple


## Class definition:


## Fields:

## Interface
class Agent:

	def __init__(self, position, init_velocity, size = 1.0, energy = 20.0, 
	sight_range = 20.0, max_speed = 5.0, max_acc = 5.0, eat_range = 1.0, max_energy = 20.0):
		self.pos = position 
		self.vel = init_velocity

		self.energy = energy
		self.max_energy = energy
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
				dists.append((euclidean, food_loc, (delta_x, delta_y)))
		
		dists.sort()

		to_eat_action = (False, (0,0))

		if len(dists) > 0:
			(min_dist, food_loc, _) = dists[0]
			closest_food = (food_loc[0] - self.pos[0], food_loc[1] - self.pos[1])
			
			if min_dist < self.eat_range:
				to_eat_action = (True, food_loc)

			a = (2 * np.array(closest_food) - self.vel)

		else:
			ax = np.random.random((1,)) - 0.5
			ay = np.random.random((1,)) - 0.5
			a = np.hstack((ax,ay))

		rel_pos = list(map(lambda x : x[2], dists))
		while 5 - len(rel_pos) > 0:
			theta = random.uniform(0,1)*2*math.pi
			rel_pos.append((self.sight_range*math.cos(theta), self.sight_range*math.sin(theta)))

		rel_pos = rel_pos[0:5]
		rel_pos = list(sum(rel_pos,())) 
		
		# ax = np.array([[1]])
		# ay = np.array([[0]])
		
		# # pack together the acceleration components
		# a = np.hstack((ax,ay))


		a = (a / np.linalg.norm(a)) * self.max_acc
		self.energy -= 0.1

		return (a, to_eat_action, rel_pos)