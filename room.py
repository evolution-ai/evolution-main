from body import Agent
import numpy as np
# import matplotlib.pyplot as plt
import pygame as pg
from visualizer import Visualizer


class Environment:
	def __init__(self):
		# Simulation parameters
		self.N         = 5       # Number of agents
		self.t         = 0       # current time of the simulation
		self.tEnd      = 1000     # time at which simulation ends
		self.dt        = 0.02    # time step size
		self.plotRealTime = True # switch on for plotting as the simulation goes along
		self.agents = []
		self.running = True
		self.gridsize = 100.0
		self.viz = Visualizer()

		self.foodN = 150
		self.food_dict = dict()

		self.initialize_positions()
		self.initialize_agents()
		self.initialize_food()
		
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

	def update(self):

		acc = np.zeros((self.N,2))
		for i, agent in enumerate(self.agents):
			(acc[i], to_eat_action) = agent.determine_next_move(self.food_dict)

			if to_eat_action[0]:
				self.food_dict.pop(to_eat_action[1])

		return acc
		
	def is_running(self):
		return self.running

	def run(self):

		# Convert to Center-of-Mass frame
		self.vel -= np.mean(self.vel)
		
		# calculate initial gravitational accelerations
		acc = self.update()

		# number of timesteps
		Nt = int(np.ceil(self.tEnd/self.dt))
		
		# save energies, particle orbits for plotting trails
		pos_save = np.zeros((self.N,2,Nt+1))
		pos_save[:,:,0] = self.pos
		

		# Simulation Main Loop
		for i in range(Nt):
			# (1/2) kick
			self.vel += acc * self.dt/2.0
			
			# drift
			self.pos += self.vel * self.dt
			
			# update accelerations
			acc = self.update()
			
			# (1/2) kick
			self.vel += acc * self.dt/2.0
			
			# update time
			self.t += self.dt
			
			# save energies, positions for plotting trail
			pos_save[:,:,i+1] = self.pos
			
			# plot in real time
			if self.plotRealTime or (i == Nt-1):
				self.viz.display(self.pos, self.food_dict)
		
		return 0

  
if __name__== "__main__":
	env = Environment()
	env.run()