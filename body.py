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

MOVE = 0
EAT = 1
REPRODUCE = 2
## Fields:

## Interface
class Agent:

	def __init__(self, position, init_velocity, size = 1.0, energy = 20.0, 
	sight_range = 20.0, max_speed = 5.0, max_acc = 5.0, eat_range = 1.0, max_energy = 20.0, can_reproduce = True, energy_consumption = 0.1):
		self.pos = position 
		self.vel = init_velocity

		self.energy_consumption = energy_consumption

		self.energy = energy
		self.max_energy = energy
		self.sight_range = sight_range
		self.max_speed = max_speed
		self.max_acc = max_acc
		self.eat_range = eat_range
		self.can_reproduce = can_reproduce

		self.lifetime = 0

		pass
		
	def is_dead(self):
		if self.energy <= 0:
			return True
		else:
			return False
	
	def reproduce(self):
		if self.energy > 0.7 * self.max_energy:
			sample = random.random() # TODO might not be uniform distribution
			if sample > 0.5:
				self.can_reproduce = True
				return
		self.can_reproduce = False

	def get_eat_move(self, food_dict):
		dists = []

		# find distance to each food within sight
		for food_loc in food_dict:

			delta_x = food_loc[0] - self.pos[0]
			delta_y = food_loc[1] - self.pos[1]
			euclidean = math.sqrt(delta_x**2 + delta_y**2)

			if euclidean < self.sight_range:
				dists.append((euclidean, food_loc, (delta_x, delta_y)))
		
		dists.sort()

		action = (MOVE, ())

		if len(dists) > 0:
			(min_dist, food_loc, _) = dists[0]
			closest_food = (food_loc[0] - self.pos[0], food_loc[1] - self.pos[1])
			
			if min_dist < self.eat_range:
				action = (EAT, food_loc)

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
		self.energy -= self.energy_consumption

		return (a, action, rel_pos)

	def get_reproduce_move(self, agent_list):
		dists = []

		# find distance to each food within sight
		for agent in agent_list:
			agent_loc = agent.pos

			delta_x = agent_loc[0] - self.pos[0]
			delta_y = agent_loc[1] - self.pos[1]
			euclidean = math.sqrt(delta_x**2 + delta_y**2)

			if euclidean < self.sight_range:
				dists.append((euclidean, agent, (delta_x, delta_y)))
		
		dists.sort()

		action = (MOVE, ())

		if len(dists) > 0:
			(_, agent, _) = dists[0]
			# closest_food = (agent_loc[0] - self.pos[0], agent_loc[1] - self.pos[1])
			
			# if min_dist < self.eat_range:
			action = (REPRODUCE, agent)

			# a = (2 * np.array(closest_food) - self.vel)

		ax = np.random.random((1,)) - 0.5
		ay = np.random.random((1,)) - 0.5
		a = np.hstack((ax,ay))

		# TODO: refactor csv writing
		rel_pos = list(map(lambda x : x[2], dists))
		while 5 - len(rel_pos) > 0:
			theta = random.uniform(0,1)*2*math.pi
			rel_pos.append((self.sight_range*math.cos(theta), self.sight_range*math.sin(theta)))

		rel_pos = rel_pos[0:5]
		rel_pos = list(sum(rel_pos,())) 

		return (a, action, rel_pos)

	# TODO: this comes from learning algorithm? 
	def get_want(self):

		return EAT

	def determine_next_move(self, food_dict, agent_list):
		self.lifetime += 1
		#TODO get this to work with sight range, energy, food locations
		# given the environment/state, figure out what to do next

		#TODO: I'm going to write basic functionality first, we need to speed up with vectorisation

		# pick between reproduce vs eating
		want = self.get_want()
		
		if want == EAT:
			return self.get_eat_move(food_dict)
		elif want == REPRODUCE:
			return self.get_reproduce_move(agent_list)

		
		