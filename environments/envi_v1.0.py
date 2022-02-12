import numpy as np
import matplotlib.pyplot as plt


def move(pos):
	ax = np.array([[1],[0],[-1]])
	ay = np.array([[1],[1],[1]])
	
	# pack together the acceleration components
	a = np.hstack((ax,ay))

	return a


def main():
	# Simulation parameters
	N         = 3     # Number of agents
	t         = 0       # current time of the simulation
	tEnd      = 3.0    # time at which simulation ends
	dt        = 0.01    # time step sizw
	plotRealTime = True # switch on for plotting as the simulation goes along
	
	# Generate Initial Conditions
	np.random.seed(17)            # set the random number generator seed
	
	pos  = np.random.randn(N,2)   # randomly selected positions and velocities
	vel  = np.zeros((N,2))
	
	# Convert to Center-of-Mass frame
	vel -= np.mean(vel)
	
	# calculate initial gravitational accelerations
	acc = move(pos)

	# number of timesteps
	Nt = int(np.ceil(tEnd/dt))
	
	# save energies, particle orbits for plotting trails
	pos_save = np.zeros((N,2,Nt+1))
	pos_save[:,:,0] = pos
	
	# prep figure
	fig = plt.figure(figsize=(10,10), dpi=80)
	grid = plt.GridSpec(3, 1, wspace=0.0, hspace=0.3)
	ax1 = plt.subplot(grid[0:4,0])
	
	# Simulation Main Loop
	for i in range(Nt):
		# (1/2) kick
		vel += acc * dt/2.0
		
		# drift
		pos += vel * dt
		
		# update accelerations
		acc = move(pos)
		
		# (1/2) kick
		vel += acc * dt/2.0
		
		# update time
		t += dt
		
		# save energies, positions for plotting trail
		pos_save[:,:,i+1] = pos
		
		# plot in real time
		if plotRealTime or (i == Nt-1):
			plt.sca(ax1)
			plt.cla()
			xx = pos_save[:,0,max(i-50,0):i+1]
			yy = pos_save[:,1,max(i-50,0):i+1]
			plt.scatter(xx,yy,s=1,color=[.7,.7,1])
			plt.scatter(pos[:,0],pos[:,1],s=10,color='blue')
			ax1.set(xlim=(-10, 10), ylim=(-10, 10))
			ax1.set_aspect('equal', 'box')
			ax1.set_xticks([-10,-8,-6,-4,-2,0,2,4,6,8,10])
			ax1.set_yticks([-10,-8,-6,-4,-2,0,2,4,6,8,10])
			
			plt.pause(0.0001)
	
	return 0

  
if __name__== "__main__":
  main()