from body import Agent
import numpy as np
import matplotlib.pyplot as plt



class Environment:
	def __init__(self):
		# Simulation parameters
		self.N         = 3       # Number of agents
		self.t         = 0       # current time of the simulation
		self.tEnd      = 3.0     # time at which simulation ends
		self.dt        = 0.01    # time step sizw
		self.plotRealTime = True # switch on for plotting as the simulation goes along
		self.agents = []
		self.running = True
		self.gridsize = 10.0

		self.foodN = 100

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
		
		self.pos  = (np.random.random_sample((self.N,2)) - 0.5)* self.gridsize  # randomly selected positions and velocities
		self.vel  = np.zeros((self.N,2))
	
	def initialize_food(self): 
		self.foodPos  = (np.random.random_sample((self.foodN,2)) - 0.5)* self.gridsize * 2
		

	def update(self):

		acc = np.zeros((self.N,2))
		for i, agent in enumerate(self.agents):
			acc[i] = agent.determine_next_move()
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
		
		# prep figure
		fig = plt.figure(figsize=(10,10), dpi=80)
		grid = plt.GridSpec(3, 1, wspace=0.0, hspace=0.3)
		ax1 = plt.subplot(grid[0:4,0])
		
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
				plt.sca(ax1)
				plt.cla()
				plt.scatter(self.foodPos[:,0],self.foodPos[:,1],s=10,color='red')
				xx = pos_save[:,0,max(i-50,0):i+1]
				yy = pos_save[:,1,max(i-50,0):i+1]
				plt.scatter(xx,yy,s=1,color=[.7,.7,1])
				plt.scatter(self.pos[:,0],self.pos[:,1],s=20,color='blue')
				ax1.set(xlim=(-self.gridsize, self.gridsize), ylim=(-self.gridsize, self.gridsize))
				ax1.set_aspect('equal', 'box')
				ax1.set_xticks(list(range(-int(self.gridsize), int(self.gridsize), int(self.gridsize/5))))
				ax1.set_yticks(list(range(-int(self.gridsize), int(self.gridsize), int(self.gridsize/5))))
				
				plt.pause(0.0001)
		
		return 0

  
if __name__== "__main__":
	env = Environment()
	env.run()