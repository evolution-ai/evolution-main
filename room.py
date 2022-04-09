from body import *
import numpy as np
# import matplotlib.pyplot as plt
import pygame as pg
from visualizer import Visualizer
import csv
import os

__PRINT_TO_CSV__ = False 

class Environment:
	def __init__(self):
		# Simulation parameters
		self.N         = 10       # Number of agents
		self.t         = 0       # current time of the simulation
		self.tEnd      = 1000     # time at which simulation ends
		self.dt        = 0.02    # time step size
		self.plotRealTime = True # switch on for plotting as the simulation goes along
		self.agents = []
		self.running = True
		self.gridsize = 100.0
		self.viz = Visualizer()

<<<<<<< Updated upstream
		self.foodN = 100
=======
		self.foodN = 250
>>>>>>> Stashed changes
		self.food_dict = dict()

		self.initialize_positions()
		self.initialize_agents()
		self.initialize_food()
		
		if __PRINT_TO_CSV__:
			if os.path.exists('output.csv'):
				self.f = open('output.csv', 'a')
				self.csv = csv.writer(self.f)
			else:
				self.f = open('output.csv', 'w')
				self.csv = csv.writer(self.f)
				self.csv.writerow(["rx1", "ry1", "rx2", "ry2", "rx3", "ry3","rx4", "ry4","rx5", "ry5", "ax", "ay", "to_eat"])
		pass

	def initialize_agents(self):
		for i in range(self.N):
			self.agents.append(Agent(self.pos[i], self.vel[i])) # TODO: determine if need to pass arguments to agent

	def initialize_positions(self):
		# Generate Initial Conditions
		# np.random.seed(17)            # set the random number generator seed
		
		self.pos  = (np.random.random_sample((self.N,2)) - 0.5) * self.gridsize  # randomly selected positions and velocities
		self.vel  = np.zeros((self.N,2))
	

	def initialize_food(self):

		food_pos = (np.random.normal(0, self.gridsize/3, (self.foodN, 2)))
		
		for i in range(self.foodN):
			self.food_dict[tuple(food_pos[i])] = 5
	

	# TODO how to account for selection / recombination 
	def new_baby_agent(self, parent1, parent2):
		position = (np.random.random_sample((1,2)) - 0.5) * self.gridsize
		velocity  = np.zeros((1,2))

		baby = Agent(position[0], velocity[0])
		
		# for parameters, sample from each parent +-1 some gaussian
		
		return baby

	def update(self):

		acc = np.zeros((self.N,2))

		reproduced = set()
		babies = []

		for i, agent in enumerate(self.agents):
			if agent in reproduced:
				continue

			(acc[i], action, rel_pos) = agent.determine_next_move(self.food_dict, self.agents)
			row = rel_pos
			row.extend([acc[i][0], acc[i][1], to_eat_action[0]])
			self.csv.writerow(row) if __PRINT_TO_CSV__ else False
			if to_eat_action[0]:
				food_energy = self.food_dict.pop(to_eat_action[1])
				agent.energy += food_energy
			elif action[0] == REPRODUCE:
				parent1 = agent
				parent2 = action[1]

				if parent2.get_want() == REPRODUCE and (parent2 not in reproduced and parent1 not in reproduced):
					reproduced.add(parent1)
					reproduced.add(parent2)
					
					new_baby = self.new_baby_agent(parent1, parent2)
					babies.append(new_baby)

		for new_baby in babies:
			self.agents.append(new_baby)
			self.N += 1
			print(self.pos.shape)
			print(new_baby.pos.shape)
			self.pos = np.append(self.pos, [new_baby.pos], axis = 0)
			self.vel = np.append(self.vel, [new_baby.vel], axis = 0)
			acc = np.append(acc, np.zeros((1,2)), axis = 0)

		return acc
		
	def is_running(self):
		return self.running

	def check_bounds(self):
		for i, agent in enumerate(self.agents):
			curr_pos = self.pos[i]

			if curr_pos[0] > self.gridsize:
				curr_pos[0] = self.gridsize
			elif curr_pos[0] < -self.gridsize:
				curr_pos[0] = -self.gridsize
			
			if curr_pos[1] > self.gridsize:
				curr_pos[1] = self.gridsize
			elif curr_pos[1] < -self.gridsize:
				curr_pos[1] = -self.gridsize

			agent.pos = curr_pos
			pass
	
	def remove_dead_agents(self):

		dead  = list(filter(lambda a: a.is_dead(), self.agents))
		for d in dead:
			print(d.lifetime)
		self.agents = list(filter(lambda a: not a.is_dead(), self.agents))

		oldN = self.N
		self.N = len(self.agents)

		if oldN != self.N:
			new_pos = np.zeros((self.N, 2))
			new_vel = np.zeros((self.N, 2))
			
			for i, agent in enumerate(self.agents):
				new_pos[i] = agent.pos
				new_vel[i] = agent.vel

			self.pos = new_pos
			self.vel = new_vel
	

	def run(self):

		# Convert to Center-of-Mass frame
		self.vel -= np.mean(self.vel)
		
		# calculate initial gravitational accelerations
		acc = self.update()

		# number of timesteps
		Nt = int(np.ceil(self.tEnd/self.dt))
		
		# save energies, particle orbits for plotting trails
		# pos_save = np.zeros((self.N,2,Nt+1))
		# pos_save[:,:,0] = self.pos
		

		# Simulation Main Loop
		for i in range(Nt):
			# (1/2) kick
			self.vel += acc * self.dt/2.0
			
			# drift
			self.pos += self.vel * self.dt

			# cull the weak
			self.remove_dead_agents()
			
			# make sure boundaries respected
			self.check_bounds()

			# update accelerations
			acc = self.update()

			
			
			# (1/2) kick
			self.vel += acc * self.dt/2.0
			
			# update time
			self.t += self.dt
			
			# save energies, positions for plotting trail
			# pos_save[:,:,i+1] = self.pos
			
			# plot in real time
			if self.plotRealTime or (i == Nt-1):
				self.viz.display(self.agents, self.food_dict)
		
		return 0

  
if __name__== "__main__":
	env = Environment()
	env.run()