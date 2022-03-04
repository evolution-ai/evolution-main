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
		global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP, DEFEND, LEFT_KAMIKAZE, RIGHT_KAMIKAZE
		WALL = config["unitInformation"][0]["shorthand"]
		SUPPORT = config["unitInformation"][1]["shorthand"]
		TURRET = config["unitInformation"][2]["shorthand"]
		SCOUT = config["unitInformation"][3]["shorthand"]
		DEMOLISHER = config["unitInformation"][4]["shorthand"]
		INTERCEPTOR = config["unitInformation"][5]["shorthand"]
		MP = 1
		SP = 0
		
		
		# MACROS FOR ATTACK STATE
		DEFEND = 0
		LEFT_KAMIKAZE = 1
		RIGHT_KAMIKAZE = 2


		# This is a good place to do initial setup
		self.scored_on_locations = []

		# 0 -> don't attack
		# 1 -> ATTACKKKKKK MFFFFFFFF DIEEEEEEEE :)
		self.attack_state = DEFEND
		
		self.opening_phase = 3
		self.mid_phase = 6
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
		
		if game_state.turn_number < self.opening_phase:
			self.early_game_strategy(game_state)

		elif game_state.turn_number == self.opening_phase:
			self.early_game_strategy(game_state)
			self.clear_early_game(game_state)

		elif game_state.turn_number < self.mid_phase:
			self.mid_game_transition(game_state)
			
		else:
			self.mid_game_strategy(game_state)

		# Submit the moves to terminal
		game_state.submit_turn()





	def early_game_strategy(self, game_state):

		opening_wall_locations = [[0, 13], [1, 13], [26, 13], [27, 13], [2, 13], [3, 13], [4, 13], 
			[23, 13], [24, 13], [25, 13], [5, 12], [8, 12], [12, 12], [15, 12], [19, 12], [22, 12]]
		game_state.attempt_spawn(WALL, opening_wall_locations)
		
		corner_turret_locations = [[4, 12], [23, 12]]
		game_state.attempt_spawn(TURRET, corner_turret_locations)

		interceptor_deploy_locations = [[5, 8], [22, 8]]
		game_state.attempt_spawn(INTERCEPTOR, interceptor_deploy_locations)

		additional_turret_locations = [[8, 11], [12, 11], [15, 11], [19, 11], [3, 12], [24, 12]]
		game_state.attempt_spawn(TURRET, additional_turret_locations)

		game_state.attempt_upgrade(corner_turret_locations)





	def mid_game_strategy(self, game_state):

		attack_MP_threshold = 13 + (game_state.turn_number // 10)
		attack_SP_threshold = 10
		PICKUP_AMOUNT = self.get_pickup_refund(game_state)

		# TODO: FIX THIS LOCATIONS
		self.build_permanent_defense(game_state)

		if self.attack_state == DEFEND: 
			self.build_temporary_defense(game_state, True)
			self.mid_game_turtly(game_state)

			SUFFICIENT_MP = game_state.get_resource(MP) > attack_MP_threshold
			SUFFICIENT_SP = game_state.get_resource(SP) + PICKUP_AMOUNT > attack_SP_threshold
			SUPPORT_SPAWNED = self.check_support_spawned(game_state)
			CHECK_KAMIKAZE = self.check_kamikaze(game_state)
			# TODO: ONLY GO INTO PREPPY IF THERE ARE ENOUGH WALLS TO FUND AN ATTACK
			if SUFFICIENT_SP and SUFFICIENT_MP and SUPPORT_SPAWNED and CHECK_KAMIKAZE:
				self.mid_game_preppy(game_state)

		elif self.attack_state == LEFT_KAMIKAZE:
			# kamikaze
			self.mid_game_kamikazy(game_state)




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




	def mid_game_transition(self, game_state):
		# Spawn Priority:
		# TODO: place_mid_defense -> add in more turrets in corner 	
		# 8 upgrade outside pinks 
		pink_turret_locations = [[12, 10], [15, 10], [8, 10], [19, 10]]
		pink_wall_locations = [[8, 11], [12, 11], [15, 11], [19, 11], [9, 10], [10, 10], [11, 10], [16, 10], [17, 10], [18, 10]]

		teal_turret_locations = [[5, 11], [22, 11]]
		teal_wall_locations = [[6, 11], [7, 11], [20, 11], [21, 11]]
		
		# 24 points in pink 
		game_state.attempt_spawn(WALL, pink_wall_locations)
		game_state.attempt_spawn(TURRET, pink_turret_locations)
		# 4 turrets to put in green 
		game_state.attempt_spawn(WALL, teal_wall_locations)
		game_state.attempt_spawn(TURRET, teal_turret_locations)

		# upgrades corner walls/ turrets 
		self.build_permanent_defense(game_state, True)
		self.build_temporary_defense(game_state, True)

		game_state.attempt_spawn(INTERCEPTOR, [[15,1], [12,1]])
		




	def mid_game_turtly(self, game_state):

		## TODO 1.) Upgrade turrets before upgrading walls 
		## 2.) corner turrets, center turrets, then others for upgrading 
		## 3.) make sure all turrets have corner walls 

		# TODO: place_mid_defense -> add in more turrets in corner 	

		# 8 upgrade outside pinks 
		pink_wall_locations = [[6, 11], [7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], [15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [20, 11], [21, 11], [22, 12]]
		pink_peri_wall = [[6, 11], [20, 11],[7, 11], [21, 11]]
		pink_center_wall = [[8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], [15, 11], [16, 11], [17, 11], [18, 11], [19, 11]]
		mid_turret_locations = [[8, 10], [12, 10]]
		peri_turret_locations = [[15, 10], [19, 10]]
		yellow_turret_locations = [[5, 11], [22, 11], [4, 11], [23, 11]]
		yellow_wall_locations = [[6, 10], [7, 10], [9, 10], [10, 10], [11, 10], [13, 10], [14, 10], [16, 10], [17, 10], [18, 10], [20, 10], [21, 10]]
		orange_turrent_locations = [[1, 12], [26, 12]]
		
		base_support_locations = [[13, 3], [14, 3]]
		extra_support_locations = [[12, 4], [13, 4], [14, 4], [15, 4]]

		# spawns turrets in the center line
		game_state.attempt_spawn(TURRET, mid_turret_locations)
		game_state.attempt_spawn(TURRET, peri_turret_locations)

		# spawns main wall 
		game_state.attempt_spawn(WALL, pink_center_wall)
		
		# upgrades corner walls/ turrets 
		self.build_permanent_defense(game_state, True)
		
		# upgrade peri turrets
		game_state.attempt_upgrade(peri_turret_locations)

		# add in two more wall units in the main line per side
		game_state.attempt_spawn(WALL, pink_peri_wall)

		# upgrade 2 center turrets
		game_state.attempt_upgrade(mid_turret_locations)

		# spawn two turrets on the peripheries
		game_state.attempt_spawn(TURRET, orange_turrent_locations)

		# add in more turrets
		game_state.attempt_spawn(TURRET, yellow_turret_locations)

		# spawn wall between turrets behind main line 
		game_state.attempt_spawn(WALL, yellow_wall_locations)
	
		game_state.attempt_spawn(SUPPORT, base_support_locations)
				
		if game_state.get_resource(SP) > 5:
			game_state.attempt_upgrade(pink_wall_locations)

		game_state.attempt_spawn(SUPPORT, extra_support_locations)
		game_state.attempt_upgrade(base_support_locations)
		game_state.attempt_upgrade(extra_support_locations)

		# spawn interceptors if gap in wall
		# check spawn points
		
		#TODO: PUT THE INTERCEPTORS AT BEST LOCATAION
		possible_end = game_state.find_path_to_edge([13,0])[-1]
		if possible_end in game_state.game_map.get_edge_locations(game_state.game_map.TOP_LEFT): 
			game_state.attempt_spawn(INTERCEPTOR, [[22,8], [23,9]])
		elif possible_end in game_state.game_map.get_edge_locations(game_state.game_map.TOP_RIGHT):
			game_state.attempt_spawn(INTERCEPTOR, [[4,9], [5,8]])


	def get_pickup_refund(self, game_state):
		yellow_wall_locations = [[6, 10], [7, 10], [9, 10], [10, 10], [11, 10], 
				[13, 10], [14, 10], [16, 10], [17, 10], [18, 10], [20, 10], [21, 10]]
		
		refund = 0
		for location in yellow_wall_locations:
			struct = game_state.contains_stationary_unit(location)
			if struct:
				if struct.unit_type == WALL:
					refund += (0.97 * game_state.type_cost(struct.unit_type)[SP] * (struct.health / struct.max_health))
		
		return refund


	def check_support_spawned(self, game_state):
		base_support_locations = [[13, 3], [14, 3]]

		for location in base_support_locations:
			struct = game_state.contains_stationary_unit(location)
			if struct:
				return True
			else:
				return False


	def check_kamikaze(self, game_state):
		wall_locations = [[2, 13], [3, 12], [4, 11], [25, 13], [24, 12], [23, 11]]

		for location in wall_locations:
			struct = game_state.contains_stationary_unit(location)
			if not struct:
				return False
		
		return True


	def mid_game_preppy(self, game_state): 
		
		self.determine_kamikaze_side(game_state)

		# TODO: PICK THE BETTER SIDE
		# prepare
		yellow_wall_locations = [[6, 10], [7, 10], [9, 10], [10, 10], [11, 10], 
			[13, 10], [14, 10], [16, 10], [17, 10], [18, 10], [20, 10], [21, 10]]
		temp_left_wall_locations = [[ 0, 13],[ 1, 13],[ 1, 12]]
		temp_right_wall_locations = [[ 26, 13],[ 27, 13],[ 26, 12]]

		if self.attack_state == LEFT_KAMIKAZE:
			game_state.attempt_remove(temp_left_wall_locations)
			
		elif self.attack_state == RIGHT_KAMIKAZE:
			game_state.attempt_remove(temp_right_wall_locations)
		else:
			gamelib.debug_write("Invalid Kamikaze state. Setting to left.")
			self.attack_state = LEFT_KAMIKAZE
			game_state.attempt_remove(temp_left_wall_locations)
			
		game_state.attempt_remove(yellow_wall_locations)
		
		# TODO: still needed?
		if game_state.get_resource(SP) < 20:
			# pink_walls_layer_two_locations = [[6, 10], [8, 10], [9, 10], [10, 10], [12, 10], [13, 10], [14, 10], [15, 10], [17, 10], [18, 10], [19, 10], [21, 10]]
			game_state.attempt_remove(yellow_wall_locations)
	
	def determine_kamikaze_side(self, game_state):
		left_corner_coords = [[0, 13], [1, 13], [1, 12], [1, 15], [0, 14], [1, 14]]
		right_corner_coords = [[26, 13], [27, 13], [26, 12], [26, 15], [26, 14], [27, 14]]

		left_damage = 0
		right_damage = 0

		for coord in left_corner_coords:
			# Get number of enemy turrets that can attack each location and multiply by turret damage
			left_damage += len(game_state.get_attackers(coord, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
		
		for coord in right_corner_coords:
			# Get number of enemy turrets that can attack each location and multiply by turret damage
			right_damage += len(game_state.get_attackers(coord, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
		
		if left_damage < right_damage:
			self.attack_state = LEFT_KAMIKAZE
		else:
			self_attack_state = RIGHT_KAMIKAZE

		



	def mid_game_kamikazy(self, game_state):
		# TODO: add in more supports in the line
		
		req_points = 10
		num_sups = 0

		interior_channel_wall_left = [[13, 2], [14, 1]]
		interior_channel_wall_right = [[13, 1], [14, 2]]

		game_state.attempt_spawn(WALL, interior_channel_wall_left)

		attack_channel_wall_left = [[12, 3], [11, 4], [10, 5], [9, 6], [8, 7], [7, 8], [6, 9], [5, 10]]
		attack_channel_wall_right = [[15, 3], [16, 4], [17, 5], [18, 6], [19, 7], [20, 8], [21, 9], [22, 10]]

		# TODO: add switching based on self.attack_state == LEFT_KAMIKAZE or self.attack_state == RIGHT_KAMIKAZE
		
		for location in attack_channel_wall_left:
			if game_state.get_resource(SP) > req_points + 3:
				game_state.attempt_spawn(SUPPORT, location)
				num_sups += 1
			else:
				game_state.attempt_spawn(WALL, location)
			req_points -= 1

		game_state.attempt_remove(interior_channel_wall_left)
		game_state.attempt_remove(attack_channel_wall_left)

		if game_state.turn_number < 45:
			game_state.attempt_spawn(SCOUT, [14, 0], 5 + num_sups)
			game_state.attempt_spawn(SCOUT, [12, 1], 1000)
		else:
			game_state.attempt_spawn(DEMOLISHER, [14, 0], 1000)

		self.attack_state = DEFEND


	
	
	# TODO: FIX THIS LOCATIONS
	def build_permanent_defense(self, game_state, upgrade = False):
		# Core defenses for all the orientations
		perm_turret_locations = [[ 3, 12],[ 4, 12],[ 23, 12],[ 24, 12]]

		# attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
		game_state.attempt_spawn(TURRET, perm_turret_locations)
		
		# Place walls in the corners to prevent attacks
		perm_wall_locations = [[ 2, 13],[ 3, 13],[ 4, 13],[ 23, 13],[ 24, 13],[ 25, 13]]
		game_state.attempt_spawn(WALL, perm_wall_locations)

		if upgrade:
			game_state.attempt_upgrade(perm_turret_locations)
			game_state.attempt_upgrade(perm_wall_locations)
			



	def build_temporary_defense(self, game_state, upgrade = False):
		
		temp_wall_locations = [[0, 13], [1, 13], [2, 13], [25, 13], [26, 13], [27, 13]]
		# temp_turrets_locations = [[1, 12], [2, 12], [25, 12], [26, 12]]
		
		game_state.attempt_spawn(WALL, temp_wall_locations)
		# game_state.attempt_spawn(TURRET, temp_turrets_locations)
		
		if upgrade:
			game_state.attempt_upgrade(temp_wall_locations)



	def clear_early_game(self, game_state):
		points_to_remove = [[6, 12], [7, 12], [8, 12], [9, 12], [10, 12], 
			[11, 12], [12, 12], [13, 12], [14, 12], [15, 12], [16, 12], [17, 12], 
			[18, 12], [19, 12], [20, 12], [21, 12], [6, 11], 
			[7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], 
			[15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [20, 11], [21, 11]]
		game_state.attempt_remove(points_to_remove)



if __name__ == "__main__":
	algo = AlgoStrategy()
	algo.start()
