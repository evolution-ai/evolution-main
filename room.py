from cProfile import label
from body import *
import numpy as np
import matplotlib.pyplot as plt
import pygame as pg
from visualizer import Visualizer
import csv
import os

__PRINT_TO_CSV__ = False


class Population:

	def __init__(self, mean_size = 10.0, std_size = 1.0, mean_max_energy = 20.0, 
		std_max_energy = 20.0, mean_sight_range = 40.0, std_sight_range = 40.0,
		mean_max_speed = 5.0, std_max_speed = 5.0, mean_max_acc = 5.0, 
		std_max_acc = 5.0, mean_behaviour = 2.0, std_behaviour = 1.0):

		self.mean_size = mean_size
		self.std_size = std_size

		self.mean_max_energy = mean_max_energy
		self.std_max_energy = std_max_energy

		self.mean_sight_range = mean_sight_range
		self.std_sight_range = std_sight_range

		self.mean_max_speed = mean_max_speed
		self.std_max_speed = std_max_speed

		self.mean_max_acc = mean_max_acc
		self.std_max_acc = std_max_acc

		self.mean_behaviour = mean_behaviour
		self.std_behaviour = std_behaviour



class Environment:

	def __init__(self, population_params, plot_real_time = True, temperature = 100):

		self.population_params = population_params

		# Simulation parameters
		self.N_init	   = 20		 # Number of agents initally
		self.N         = self.N_init   # agents alive now
		self.t         = 0       # current time of the simulation
		self.tEnd      = 100     # time at which simulation ends
		self.dt        = 0.02    # time step size
		self.plotRealTime = plot_real_time # switch on for plotting as the simulation goes along
		self.agents = []
		self.running = True
		self.gridsize = 100.0

		if plot_real_time:
			self.viz = Visualizer()

		self.foodN = 1000
		self.food_dict = dict()

		self.initialize_positions()
		self.initialize_agents()
		self.initialize_food()

		self.dead_agents = []
		
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

		mean_size = self.population_params.mean_size
		std_size = self.population_params.std_size

		mean_max_energy = self.population_params.mean_max_energy
		std_max_energy = self.population_params.std_max_energy

		mean_sight_range = self.population_params.mean_sight_range
		std_sight_range = self.population_params.std_sight_range

		mean_max_speed = self.population_params.mean_max_speed
		std_max_speed = self.population_params.std_max_speed

		mean_max_acc = self.population_params.mean_max_acc
		std_max_acc = self.population_params.std_max_acc

		mean_behaviour = self.population_params.mean_behaviour
		std_behaviour = self.population_params.std_behaviour

		for i in range(self.N):

			size = np.random.normal(mean_size, std_size)
			if size < 1: size = 1

			max_energy = np.random.normal(mean_max_energy, std_max_energy)
			if max_energy < 1: max_energy = 1

			sight_range = np.random.normal(mean_sight_range, std_sight_range)
			if sight_range < 1: sight_range = 1

			max_speed = np.random.normal(mean_max_speed, std_max_speed)
			if max_speed < 1: max_speed = 1

			max_acc = np.random.normal(mean_max_acc, std_max_acc)
			if max_acc < 1: max_acc = 1

			behaviour = np.random.normal(mean_behaviour, std_behaviour)
			if behaviour < 1: behaviour = 1

			self.agents.append(Agent(position=self.pos[i], init_velocity=self.vel[i], size=size, energy=max_energy, sight_range=sight_range, max_speed=max_speed, max_acc=max_acc, max_energy=max_energy, behavioural=behaviour, agent_id=i+1)) # TODO: determine if need to pass arguments to agent


	def initialize_positions(self):
		# Generate Initial Conditions
		# np.random.seed(17)            # set the random number generator seed
		
		self.pos  = (np.random.random_sample((self.N,2)) - 0.5) * self.gridsize  # randomly selected positions and velocities
		self.vel  = np.zeros((self.N,2))
	

	def initialize_food(self):

		food_pos = (np.random.normal(0, self.gridsize/3, (self.foodN, 2)))
		
		for i in range(self.foodN):
			self.food_dict[tuple(food_pos[i])] = np.random.normal(4, 1)
	

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
			row.extend([acc[i][0], acc[i][1], action[0]])

			if __PRINT_TO_CSV__:
				self.csv.writerow(row)

			if action[0] == EAT:
				food_energy = self.food_dict.pop(action[1])
				agent.energy += food_energy

				if agent.energy > agent.max_energy:
					agent.energy = agent.max_energy


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
			self.dead_agents.append(d)
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
			if self.plotRealTime:
				self.viz.display(self.agents, self.food_dict)
			else:
				if i % 250 == 0: print(int(i/Nt * 100), "% Complete")

		self.agents = sorted(self.agents, key=lambda a: a.energy, reverse=True)
		self.dead_agents = sorted(self.dead_agents, key=lambda a: a.lifetime, reverse=True)

		alive_agents = len(self.agents)
		parent_count = 6

		if alive_agents > parent_count: 
			self.agents = self.agents[0:parent_count]
		else:
			num_to_reserrect = parent_count - alive_agents
			self.agents += self.dead_agents[0:num_to_reserrect]


		size_array = np.zeros((parent_count,))
		energy_array = np.zeros((parent_count,))
		sight_array = np.zeros((parent_count,))
		speed_array = np.zeros((parent_count,))
		acc_array = np.zeros((parent_count,))
		behaviour_array = np.zeros((parent_count,))
		lifespan_array = np.zeros((parent_count,))

		for i, agent in enumerate(self.agents):

			# agent.display_agent()

			size_array[i] = agent.size
			energy_array[i] = agent.max_energy
			sight_array[i] = agent.sight_range
			speed_array[i] = agent.max_speed
			acc_array[i] = agent.max_acc
			behaviour_array[i] = agent.behavioural
		

		new_population_parameters = Population(
			mean_size=np.mean(size_array),
			std_size=np.std(size_array),
			mean_max_energy=np.mean(energy_array),
			std_max_energy=np.std(energy_array),
			mean_sight_range=np.mean(sight_array),
			std_sight_range=np.std(sight_array),
			mean_max_speed=np.mean(speed_array),
			std_max_speed=np.std(speed_array),
			mean_max_acc=np.mean(acc_array),
			std_max_acc=np.std(acc_array),
			mean_behaviour=np.mean(behaviour_array),
			std_behaviour=np.std(behaviour_array)
			)

		return new_population_parameters, np.mean(lifespan_array)


def main():

	print("\n")

	generations = 20

	initial_size = 20
	initial_energy = 20
	initial_sight = 20
	initial_speed = 5
	initial_acc = 5
	initial_behaviour = 2

	size_vs_time = np.zeros((generations+1, ))
	energy_vs_time = np.zeros((generations+1, ))
	sight_vs_time = np.zeros((generations+1, ))
	speed_vs_time = np.zeros((generations+1, ))
	acc_vs_time = np.zeros((generations+1, ))
	behaviour_vs_time = np.zeros((generations+1, ))

	size_vs_time[0] = initial_size
	energy_vs_time[0] = initial_energy
	sight_vs_time[0] = initial_sight
	speed_vs_time[0] = initial_speed
	acc_vs_time[0] = initial_acc
	behaviour_vs_time[0] = initial_behaviour

	current_population = Population(initial_size, 8, initial_energy, 8, initial_sight, 8, initial_speed, 2, initial_acc, 2, initial_behaviour, 0.5)

	for gen in range(generations):

		print("GENERATION:", gen)

		env = Environment(current_population, True)
		current_population, mean_life = env.run()

		size_vs_time[gen+1] = (current_population.mean_size)
		energy_vs_time[gen+1] = (current_population.mean_max_energy)
		sight_vs_time[gen+1] = (current_population.mean_sight_range)
		speed_vs_time[gen+1] = (current_population.mean_max_speed)
		acc_vs_time[gen+1] = (current_population.mean_max_acc)
		behaviour_vs_time[gen+1] = (current_population.mean_behaviour)

		print("\n")

	size_vs_time /= initial_size
	energy_vs_time /= initial_energy
	sight_vs_time /= initial_sight
	speed_vs_time /= initial_speed
	acc_vs_time /= initial_acc
	behaviour_vs_time /= initial_behaviour

	plt.plot(size_vs_time, label = "Size")
	# plt.plot(energy_vs_time, label = "Max Energy")
	plt.plot(sight_vs_time, label = "Max Sight Range")
	plt.plot(speed_vs_time, label = "Max Speed")
	plt.plot(acc_vs_time, label = "Max Accelaration")
	plt.plot(behaviour_vs_time, label = "Behaviour")
	plt.legend()
	plt.xlabel("Generation")
	plt.ylabel("Value (Relative to Initial)")
	title_string = "Simple Evol: " + "Agents = " + str(env.N_init) + ", Food = " + str(env.foodN)
	plt.title(title_string)
	plt.show()

if __name__== "__main__":
	main()
	