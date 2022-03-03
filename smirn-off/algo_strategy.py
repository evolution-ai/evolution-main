import gamelib
import random
import math
import warnings
from sys import maxsize
import json
from algo_util import AlgoUtil


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):


	def __init__(self):
		super().__init__()
		seed = random.randrange(maxsize)
		random.seed(seed)
		gamelib.debug_write('Random seed: {}'.format(seed))
		self.algo_util = AlgoUtil()

	def on_game_start(self, config):
		""" 
		Read in config and perform any initial setup here 
		"""
		gamelib.debug_write('Configuring your custom algo strategy...')
		self.config = config
		global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
		WALL = config["unitInformation"][0]["shorthand"]
		SUPPORT = config["unitInformation"][1]["shorthand"]
		TURRET = config["unitInformation"][2]["shorthand"]
		SCOUT = config["unitInformation"][3]["shorthand"]
		DEMOLISHER = config["unitInformation"][4]["shorthand"]
		INTERCEPTOR = config["unitInformation"][5]["shorthand"]
		MP = 1
		SP = 0
		# This is a good place to do initial setup
		self.scored_on_locations = []

		# 0 -> don't attack
		# 1 -> ATTACKKKKKK MFFFFFFFF DIEEEEEEEE :)
		self.attack_state = 0
		
		self.mid_phase = 4
		self.late_phase = 0


	def on_turn(self, turn_state):
		"""
		This function is called every turn with the game state wrapper as
		an argument. The wrapper stores the state of the arena and has methods
		for querying its state, allocating your current resources as planned
		unit deployments, and transmitting your intended deployments to the
		game engine.
		"""
		game_state = gamelib.GameState(self.config, turn_state)

		gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
		game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.
		
		if game_state.turn_number < self.mid_phase:
			self.early_game_strategy(game_state)

		elif game_state.turn_number == self.mid_phase:
			self.early_game_strategy(game_state)
			self.clear_early_game(game_state)

		else:
			self.mid_game_strategy(game_state)

		# TODO: GO FOR THE HEAD (ENDGAME)

		# Submit the moves to terminal
		game_state.submit_turn()



	def early_game_strategy(self, game_state):
		
		self.build_permanent_defense(game_state)

		deploy_locations = [[5, 8], [22, 8]]
		game_state.attempt_spawn(INTERCEPTOR, deploy_locations)

		additional_wall_locations = [[5, 11], [6, 11], [21, 11], [22, 11]]
		game_state.attempt_spawn(WALL, additional_wall_locations)

		# Core defenses for all the orientations
		opening_turret_locations = [[3, 12], [24, 12], [11, 10], [16, 10], [7, 10], [20, 10]]
		game_state.attempt_upgrade(opening_turret_locations)




	def mid_game_strategy(self, game_state):

		attack_threshold = 14

		# build the main game defenses
		self.build_permanent_defense(game_state)

		if not self.attack_state:
			self.build_temporary_defense(game_state)


		# TODO: select a mid game defense strategy
		self.mid_game_zelensky(game_state)


		# if not self.attack_state and game_state.get_resource(MP) > attack_threshold:
		# 	# prepare
		# 	self.attack_state = 1

		# elif self.attack_state:
		# 	# kamikaze
		# 	self.attack_state = 0





	def mid_game_zelensky(self, game_state): 
		# Spawn Priority: 
		
		# PINK = long wall/turrets
		pink_wall_locations = [[10, 12], [11, 12], [12, 12], [13, 12], [14, 12], 
								[15, 12], [16, 12], [17, 12], [18, 12], [19, 12], 
								[20, 12], [21, 12], [22, 12], [4, 11], [5, 10]]
		pink_turret_locations = [[6, 10], [8, 10]]
		game_state.attempt_spawn(WALL, pink_wall_locations)
		game_state.attempt_spawn(TURRET, pink_turret_locations)

		# YELLOW = extra wall length/ turret / support 
		yellow_wall_locations = [[7, 12], [8, 12], [9, 12]]
		yellow_turret_locations = [[9, 10], [10, 10], [12, 10], [13, 10], [18, 10], [22, 10]]
		yellow_support_locations = [[14, 9], [15, 9], [17, 9], [19, 9]]

		game_state.attempt_spawn(WALL, yellow_wall_locations)
		self.build_permanent_defense(game_state, upgrade=True)

		game_state.attempt_spawn(TURRET, yellow_turret_locations)
		game_state.attempt_spawn(SUPPORT, yellow_support_locations)
		
		# ORANGE = extra turret + extra support 
		orange_turret_locations = [[14, 10], [15, 10], [17, 10], [19, 10]]
		orange_support_locations = [[23, 11], [18, 9], [18, 8], [19, 8]]

		game_state.attempt_upgrade(pink_turret_locations)
		game_state.attempt_upgrade(pink_wall_locations)

		game_state.attempt_spawn(TURRET, orange_turret_locations)
		game_state.attempt_spawn(SUPPORT, orange_support_locations)

		game_state.attempt_upgrade(yellow_support_locations)
		game_state.attempt_upgrade(yellow_wall_locations)
		game_state.attempt_upgrade(yellow_turret_locations)

		game_state.attempt_upgrade(orange_support_locations)
		game_state.attempt_upgrade(orange_turret_locations)



	



	def mid_game_turtly(self, game_state):
		# Spawn Priority:
		pass




	def mid_game_kamikazy(self, game_state):
		pass


	
	

	def build_permanent_defense(self, game_state, upgrade = False):
		# Core defenses for all the orientations
		opening_wall_locations = [[0, 13], [1, 13], [2, 13], [3, 13], [24, 13], [25, 13], 
			[26, 13], [27, 13], [4, 12], [23, 12], [7, 11], [11, 11], [16, 11], [20, 11]]
		game_state.attempt_spawn(WALL, opening_wall_locations)

		# Core defenses for all the orientations
		opening_turret_locations = [[3, 12], [24, 12], [11, 10], [16, 10], [7, 10], [20, 10]]
		game_state.attempt_spawn(TURRET, opening_turret_locations)

		if upgrade:
			game_state.attempt_upgrade(opening_turret_locations)
			game_state.attempt_upgrade(opening_wall_locations)
			



	def build_temporary_defense(self, game_state, upgrade = False):
		
		temp_wall_locations = [[0, 13], [1, 13], [2, 13], [25, 13], [26, 13], [27, 13]]
		temp_turrets_locations = [[1, 12], [2, 12], [25, 12], [26, 12]]
		
		game_state.attempt_spawn(WALL, temp_wall_locations)
		game_state.attempt_spawn(TURRET, temp_turrets_locations)
		
		if upgrade:
			game_state.attempt_upgrade(temp_wall_locations)



	def clear_early_game(game_state):
		points_to_remove = [[5, 11], [6, 11], [7, 11], [11, 11], [16, 11], [20, 11], [21, 11], [22, 11]]
		game_state.attempt_remove(points_to_remove)



if __name__ == "__main__":
	algo = AlgoStrategy()
	algo.start()
