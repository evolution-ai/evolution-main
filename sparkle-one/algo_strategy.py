from xml.dom.minidom import parseString
import gamelib
import random
import math
import warnings
from sys import maxsize
import json


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
	

		# MACROS FOR DIRECTION

		global LEFT, RIGHT
		LEFT = -1
		RIGHT = 1


		# MACROS FOR STRUCTURE FEATURE
		global DEEP_V, SHALLOW_V, RAILGUN, WEAK_LEFT_LINE, WEAK_RIGHT_LINE, FRONTAL_WALLS, STRONG_LEFT_CLUSTER, STRONG_RIGHT_CLUSTER, WEAK_LEFT_CLUSTER, WEAK_RIGHT_CLUSTER

		DEEP_V = 0
		SHALLOW_V = 1
		RAILGUN = 2
		WEAK_LEFT_LINE = 3
		WEAK_RIGHT_LINE = 4
		FRONTAL_WALLS = 5
		STRONG_LEFT_CLUSTER = 6
		STRONG_RIGHT_CLUSTER = 7
		WEAK_LEFT_CLUSTER = 8
		WEAK_RIGHT_CLUSTER = 9


		# MACROS FOR ATTACK STATE
		global OPENING_MODE, DEFEND_MODE, DESTROY_MODE, KAMIKAZE_LEFT_MODE, KAMIKAZE_RIGHT_MODE, COUNTER_RAILGUN_MODE
		OPENING_MODE = 0
		DEFEND_MODE = 1

		self.algo_mode = OPENING_MODE

		self.early_phase = 4

		self.scored_on_locations = []
		self.turret_repair_list = []
		self.wall_repair_list = []

		self.reactionary_turrets = []
		self.opponent_structure_history = []

		self.convolutional_filter_bank = self.create_convolutional_filter_bank()



	def on_turn(self, turn_state):

		game_state = gamelib.GameState(self.config, turn_state)

		# gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
		game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

		self.predict_enemy_shape(game_state)
		
		if self.algo_mode == OPENING_MODE:
			self.early_game_strategy(game_state)

		elif self.algo_mode == DEFEND_MODE or self.algo_mode == DESTROY_MODE:
			self.mid_game_strategy(game_state)
			
		# Submit the moves to terminal
		game_state.submit_turn()




	#TODO: release the interceptors
	def early_game_strategy(self, game_state):

		# central turrets and corner turrets
		central_turrets_locations = [[7, 10], [11, 10], [16, 10], [20, 10]]
		corner_turrets_loctaions = [[3, 12], [24, 12]]

		opening_turrets_loctaions = central_turrets_locations + corner_turrets_loctaions
		game_state.attempt_spawn(TURRET, opening_turrets_loctaions)
		
		opening_wall_locations = [[7, 11], [11, 11], [16, 11], [20, 11]]
		corner_wall_locations = [[0, 13], [2, 13], [3, 13], [24, 13], [25, 13], [27, 13]]
		flank_wall_locations = [[1, 13], [26, 13], [4, 12], [23, 12], [5, 11], [6, 11], [9, 11], [10, 11], [17, 11], [18, 11], [21, 11], [22, 11]]

		game_state.attempt_spawn(WALL, opening_wall_locations)
		game_state.attempt_spawn(WALL, corner_wall_locations)

		# these are permanent -- upgrade is worth it
		game_state.attempt_upgrade(corner_turrets_loctaions)

		game_state.attempt_spawn(WALL, flank_wall_locations)
		game_state.attempt_upgrade(opening_turrets_loctaions)

		# more fun walls
		game_state.attempt_spawn(INTERCEPTOR, [[7, 6], [20, 6]])

		# Clear out everything if we are at the transition turn
		if game_state.turn_number == self.early_phase:
			game_state.attempt_remove([[1, 13], [5, 11], [22, 11], [26, 13]])
			self.algo_mode = DEFEND_MODE
			
			





	# def mid_game_strategy(self, game_state):

	# 	# TODO: determine direction -- right now only right side implemented

	# 	attack_MP_threshold = 12 + (game_state.turn_number // 14)
	# 	attack_SP_threshold = 9 - (game_state.turn_number // 20)
	# 	# PICKUP_AMOUNT = self.get_pickup_refund(game_state)

	# 	# TODO: Allow the corners to open up for a kamikaze attack
	# 	self.mid_game_main_defense(game_state)
	




	def mid_game_strategy(self, game_state):

		if self.turret_repair_list:
			game_state.attempt_spawn(TURRET, self.turret_repair_list)
			self.turret_repair_list = []

		if self.wall_repair_list:
			game_state.attempt_spawn(WALL, self.wall_repair_list)
			self.wall_repair_list = []


		corner_wall_locations_1 = [[0, 13], [2, 13], [3, 13], [24, 13], [25, 13], [27, 13]]
		game_state.attempt_spawn(WALL, corner_wall_locations_1)

		main_flank_turrets_locations = [[3, 12], [24, 12]]
		game_state.attempt_spawn(TURRET, main_flank_turrets_locations)

		main_central_turrets_locations = [[7, 10], [11, 10], [16, 10], [20, 10]]
		game_state.attempt_spawn(TURRET, main_central_turrets_locations)

		main_wall_locations_1 = [[7, 11], [11, 11], [16, 11], [20, 11]]
		game_state.attempt_spawn(WALL, main_wall_locations_1)

		flank_wall_locations_1 = [[4, 12], [23, 12], [6, 11], [9, 11], [10, 11], [17, 11], [18, 11], [21, 11], [12, 10], [15, 10]]
		game_state.attempt_spawn(WALL, flank_wall_locations_1)


		self.mid_game_counter_spawn(game_state)


		game_state.attempt_upgrade(main_flank_turrets_locations)
		game_state.attempt_upgrade(main_central_turrets_locations)


		game_state.attempt_upgrade(main_wall_locations_1)


		main_support_locations = [[11, 9], [16, 9], [9, 9], [18, 9]]


		for i in range(2):
			game_state.attempt_spawn(SUPPORT, main_support_locations[i])
			game_state.attempt_upgrade(main_support_locations[i])


		game_state.attempt_upgrade(corner_wall_locations_1)


		# TODO: THESE NEED TO BE REACTIVELY GENERATED
		# Maybe a priority queue of locations with how good they are?
		# base the riority on the centre of mass of the walls lifted for repair
		flank_turret_locations = [[6, 10], [21, 10], [4, 11], [23, 11]]

		for i in range(2):
			game_state.attempt_spawn(TURRET, flank_turret_locations[i])
			game_state.attempt_upgrade(flank_turret_locations[i])


		for i in range(2, 4):
			game_state.attempt_spawn(SUPPORT, main_support_locations[i])
			game_state.attempt_upgrade(main_support_locations[i])


		game_state.attempt_upgrade(corner_wall_locations_1)


		for i in range(2, 4):
			game_state.attempt_spawn(TURRET, flank_turret_locations[i])
			game_state.attempt_upgrade(flank_turret_locations[i])




		all_turret_locations = (main_flank_turrets_locations + main_central_turrets_locations
			+ flank_turret_locations)

		for location in all_turret_locations:
			turret = game_state.contains_stationary_unit(location)
			if turret and turret.health < 0.4 * turret.max_health: 
				self.turret_repair_list.append(location)
				game_state.attempt_remove(location)


		# TODO: Wall repairs
		all_wall_locations = (main_wall_locations_1 + corner_wall_locations_1 
			+ flank_wall_locations_1)

		for location in all_wall_locations:
			wall = game_state.contains_stationary_unit(location)
			if wall and wall.health < 0.3 * wall.max_health: 
				self.wall_repair_list.append(location)
				game_state.attempt_remove(location)









	def mid_game_counter_spawn(self, game_state):

		attack_MP_threshold = 12 + (game_state.turn_number // 14)
		lowest_damage_threshold = 10



		attack_dynamic_walls = [[1, 13], [26, 13], [5, 11], [22, 11], [8, 10], [19, 10], [13, 9], [14, 9]]

		left_corner_piece = [1, 13]
		right_corner_piece = [26, 13]

		left_flank_piece = [5, 11]
		right_flank_piece = [22, 11]

		wall_to_not_build = []



		left_test_spawns = [[2, 11], [5, 8], [8, 5], [11, 2]]
		right_test_spawns = [[25, 11], [22, 8], [19, 5], [16, 2]]
		test_spawn_locations = left_test_spawns + right_test_spawns

		lowest_damage_amount, lowest_damage_spawn_location = self.least_damage_spawn_location(game_state, test_spawn_locations)

		lowest_damage_path = game_state.find_path_to_edge(lowest_damage_spawn_location)
		check_scout_pathing = lowest_damage_path[-1] in game_state.game_map.get_edge_locations(game_state.get_target_edge(lowest_damage_spawn_location))

		gamelib.debug_write("Lowest possible damage is: {}, from location {}".format(lowest_damage_amount, lowest_damage_spawn_location))



		


		# TODO: KAMIKAZE ATTACKS AND ALSO THE INTERCEPTORS AND ALSO THE STRUCTURE MEMORY AND ALSO THE CENTRE OPEN
		if lowest_damage_amount < 2 and game_state.get_resource(MP) > (attack_MP_threshold // 2) and check_scout_pathing:
			
			if lowest_damage_spawn_location in left_test_spawns:
				wall_to_not_build = right_flank_piece
			else:
				wall_to_not_build = left_flank_piece

			game_state.attempt_spawn(SCOUT, lowest_damage_spawn_location, 1000)


		elif game_state.get_resource(MP) > attack_MP_threshold:
			
			if lowest_damage_spawn_location in left_test_spawns:
				wall_to_not_build = right_flank_piece
			else:
				wall_to_not_build = left_flank_piece
			game_state.attempt_spawn(DEMOLISHER, lowest_damage_spawn_location, 1000)


		else:
			game_state.attempt_spawn(INTERCEPTOR, [[1, 12], [26, 12]])




		for wall_location in attack_dynamic_walls:
			if wall_location != wall_to_not_build:
				game_state.attempt_spawn(WALL, wall_location)

		game_state.attempt_remove(attack_dynamic_walls)










	def least_damage_spawn_location(self, game_state, location_options):
		"""
		This function will help us guess which location is the safest to spawn moving units from.
		It gets the path the unit will take then checks locations on that path to 
		estimate the path's damage risk.
		"""
		damages = []
		# Get the damage estimate each path will take
		for location in location_options:
			path = game_state.find_path_to_edge(location)
			damage = 0
			for path_location in path:
				# Get number of enemy turrets that can attack each location and multiply by turret damage
				damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
			damages.append(damage)
		
		# Now just return the location that takes the least damage
		lowest_damage_amount = min(damages)
		lowest_damage_spawn_location = location_options[damages.index(min(damages))]
		return lowest_damage_amount, lowest_damage_spawn_location
	




	def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
		total_units = 0
		for location in game_state.game_map:
			if game_state.contains_stationary_unit(location):
				for unit in game_state.game_map[location]:
					if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
						total_units += 1
		return total_units




	def predict_enemy_shape(self, game_state):

		enemy_structure = self.get_all_enemy_structures(game_state)
		filter_results = dict()
		features = []

		for i in range(10):
			filter_results[i] = self.apply_convolution(game_state, enemy_structure, i)
			features.append(0)


		if filter_results[DEEP_V] >= 8:
			gamelib.debug_write("DEEP_V")
			features[DEEP_V] = 1
		
		if filter_results[SHALLOW_V] >= 8:
			gamelib.debug_write("SHALLOW_V")
			features[SHALLOW_V] = 1
		
		if filter_results[RAILGUN] >= 15:
			gamelib.debug_write("RAILGUN")
			features[RAILGUN] = 1
		
		if filter_results[WEAK_LEFT_LINE] >= 9:
			gamelib.debug_write("WEAK_LEFT_LINE")
			features[WEAK_LEFT_LINE] = 1
		
		if filter_results[WEAK_RIGHT_LINE] >= 9:
			gamelib.debug_write("WEAK_RIGHT_LINE")
			features[WEAK_RIGHT_LINE] = 1
		
		if filter_results[FRONTAL_WALLS] >= 14:
			gamelib.debug_write("FRONTAL_WALLS")
			features[FRONTAL_WALLS] = 1
		
		if filter_results[STRONG_LEFT_CLUSTER] >= 6:
			gamelib.debug_write("STRONG_LEFT_CLUSTER")
			features[STRONG_LEFT_CLUSTER] = 1
	
		if filter_results[STRONG_RIGHT_CLUSTER] >= 6:
			gamelib.debug_write("STRONG_RIGHT_CLUSTER")
			features[STRONG_RIGHT_CLUSTER] = 1

		if filter_results[WEAK_LEFT_CLUSTER] >= 4:
			gamelib.debug_write("WEAK_LEFT_CLUSTER")
			features[WEAK_LEFT_CLUSTER] = 1
		
		if filter_results[WEAK_RIGHT_CLUSTER] >= 4:
			gamelib.debug_write("WEAK_RIGHT_CLUSTER")
			features[WEAK_RIGHT_CLUSTER] = 1



		self.opponent_structure_history.append(features)

	



	def apply_convolution(self, game_state, enemy_structure, filter_number):

		score = 0

		for location in enemy_structure:
			if location in self.convolutional_filter_bank[filter_number][1]:
				score += 1
			elif location in self.convolutional_filter_bank[filter_number][-1]:
				score -= 1

		return score







	def create_convolutional_filter_bank(self):

		filter_bank = dict()

		for i in range(10):
			filter_bank[i] = {1: set(), -1: set()}

		filter_bank[DEEP_V][1] = set([(10, 22), (11, 22), (12, 22), (13, 22), (14, 22), (15, 22), (16, 22), (17, 22), (9, 21), (10, 21), (11, 21), (12, 21), (13, 21), (14, 21), (15, 21), (16, 21), (17, 21), (18, 21), (8, 20), (9, 20), (18, 20), (19, 20), (7, 19), (8, 19), (19, 19), (20, 19), (7, 18), (8, 18), (19, 18), (20, 18), (6, 17), (7, 17), (20, 17), (21, 17), (5, 16), (6, 16), (21, 16), (22, 16)])
		filter_bank[DEEP_V][-1] = set([(12, 19), (13, 19), (14, 19), (15, 19), (11, 18), (12, 18), (13, 18), (14, 18), (15, 18), (16, 18), (11, 17), (12, 17), (13, 17), (14, 17), (15, 17), (16, 17), (10, 16), (11, 16), (12, 16), (13, 16), (14, 16), (15, 16), (16, 16), (17, 16), (10, 15), (11, 15), (12, 15), (13, 15), (14, 15), (15, 15), (16, 15), (17, 15), (10, 14), (11, 14), (12, 14), (13, 14), (14, 14), (15, 14), (16, 14), (17, 14)])

		filter_bank[SHALLOW_V][1] = set([(7, 18), (8, 18), (9, 18), (10, 18), (11, 18), (12, 18), (13, 18), (14, 18), (15, 18), (16, 18), (17, 18), (18, 18), (19, 18), (20, 18), (5, 17), (6, 17), (7, 17), (8, 17), (9, 17), (10, 17), (11, 17), (12, 17), (13, 17), (14, 17), (15, 17), (16, 17), (17, 17), (18, 17), (19, 17), (20, 17), (21, 17), (22, 17), (4, 16), (5, 16), (6, 16), (7, 16), (8, 16), (9, 16), (18, 16), (19, 16), (20, 16), (21, 16), (22, 16), (23, 16), (2, 15), (3, 15), (4, 15), (23, 15), (24, 15), (25, 15), (0, 14), (1, 14), (2, 14), (3, 14), (24, 14), (25, 14), (26, 14), (27, 14)])
		filter_bank[SHALLOW_V][-1] = set([(11, 25), (12, 25), (13, 25), (14, 25), (15, 25), (16, 25), (11, 24), (12, 24), (13, 24), (14, 24), (15, 24), (16, 24), (10, 23), (11, 23), (12, 23), (13, 23), (14, 23), (15, 23), (16, 23), (17, 23), (10, 22), (11, 22), (12, 22), (13, 22), (14, 22), (15, 22), (16, 22), (17, 22), (9, 21), (10, 21), (11, 21), (12, 21), (13, 21), (14, 21), (15, 21), (16, 21), (17, 21), (18, 21), (7, 20), (8, 20), (9, 20), (10, 20), (11, 20), (12, 20), (13, 20), (14, 20), (15, 20), (16, 20), (17, 20), (18, 20), (19, 20), (20, 20), (10, 15), (11, 15), (12, 15), (13, 15), (14, 15), (15, 15), (16, 15), (17, 15), (7, 14), (8, 14), (9, 14), (10, 14), (11, 14), (12, 14), (13, 14), (14, 14), (15, 14), (16, 14), (17, 14), (18, 14), (19, 14), (20, 14)])
	
		filter_bank[RAILGUN][1] = set([(13, 27), (14, 27), (12, 26), (13, 26), (14, 26), (15, 26), (12, 25), (13, 25), (14, 25), (15, 25), (12, 24), (13, 24), (14, 24), (15, 24), (12, 23), (13, 23), (14, 23), (15, 23), (12, 22), (13, 22), (14, 22), (15, 22), (12, 21), (13, 21), (14, 21), (15, 21), (12, 20), (13, 20), (14, 20), (15, 20), (12, 19), (13, 19), (14, 19), (15, 19), (12, 18), (13, 18), (14, 18), (15, 18), (12, 17), (13, 17), (14, 17), (15, 17), (12, 16), (13, 16), (14, 16), (15, 16), (12, 15), (13, 15), (14, 15), (15, 15)])
		filter_bank[RAILGUN][-1] = set([(9, 23), (18, 23), (8, 22), (9, 22), (18, 22), (19, 22), (7, 21), (8, 21), (9, 21), (18, 21), (19, 21), (20, 21), (6, 20), (7, 20), (8, 20), (9, 20), (18, 20), (19, 20), (20, 20), (21, 20), (5, 19), (6, 19), (7, 19), (8, 19), (9, 19), (18, 19), (19, 19), (20, 19), (21, 19), (22, 19), (4, 18), (5, 18), (6, 18), (7, 18), (8, 18), (9, 18), (18, 18), (19, 18), (20, 18), (21, 18), (22, 18), (23, 18), (3, 17), (4, 17), (5, 17), (6, 17), (7, 17), (8, 17), (9, 17), (18, 17), (19, 17), (20, 17), (21, 17), (22, 17), (23, 17), (24, 17), (2, 16), (3, 16), (4, 16), (5, 16), (6, 16), (7, 16), (8, 16), (9, 16), (18, 16), (19, 16), (20, 16), (21, 16), (22, 16), (23, 16), (24, 16), (25, 16), (1, 15), (2, 15), (3, 15), (4, 15), (5, 15), (6, 15), (7, 15), (8, 15), (9, 15), (18, 15), (19, 15), (20, 15), (21, 15), (22, 15), (23, 15), (24, 15), (25, 15), (26, 15), (1, 14), (2, 14), (3, 14), (4, 14), (5, 14), (6, 14), (7, 14), (8, 14), (9, 14), (18, 14), (19, 14), (20, 14), (21, 14), (22, 14), (23, 14), (24, 14), (25, 14), (26, 14)])

		filter_bank[WEAK_LEFT_LINE][1] = set([(9, 23), (8, 22), (7, 21), (6, 20), (5, 19), (4, 18), (3, 17), (2, 16), (1, 15), (0, 14)])
		filter_bank[WEAK_LEFT_LINE][-1] = set([(9, 22), (8, 21), (7, 20), (6, 19), (5, 18), (4, 17), (3, 16), (2, 15)])

		filter_bank[WEAK_RIGHT_LINE][1] = set([(18, 23), (19, 22), (20, 21), (21, 20), (22, 19), (23, 18), (24, 17), (25, 16), (26, 15), (27, 14)])
		filter_bank[WEAK_RIGHT_LINE][-1] = set([(18, 22), (19, 21), (20, 20), (21, 19), (22, 18), (23, 17), (24, 16), (25, 15), (26, 14)])

		filter_bank[FRONTAL_WALLS][1] = set([(4, 14), (5, 14), (6, 14), (7, 14), (8, 14), (9, 14), (10, 14), (11, 14), (12, 14), (13, 14), (14, 14), (15, 14), (16, 14), (17, 14), (18, 14), (19, 14), (20, 14), (21, 14), (22, 14), (23, 14)])
		filter_bank[FRONTAL_WALLS][-1] = set([(5, 15), (6, 15), (7, 15), (8, 15), (9, 15), (10, 15), (11, 15), (12, 15), (13, 15), (14, 15), (15, 15), (16, 15), (17, 15), (18, 15), (19, 15), (20, 15), (21, 15), (22, 15)])

		filter_bank[STRONG_LEFT_CLUSTER][1] = set([(3, 17), (4, 17), (5, 17), (2, 16), (3, 16), (4, 16), (5, 16), (1, 15), (2, 15), (3, 15), (4, 15), (5, 15), (0, 14), (1, 14), (2, 14), (3, 14), (4, 14)])
		filter_bank[STRONG_LEFT_CLUSTER][-1] = set([(13, 27), (12, 26), (13, 26), (11, 25), (12, 25), (13, 25), (10, 24), (11, 24), (12, 24), (9, 23), (10, 23), (11, 23), (8, 22), (9, 22), (10, 22), (7, 21), (8, 21), (9, 21), (6, 20), (7, 20), (8, 20), (5, 19), (6, 19), (7, 19)])

		filter_bank[STRONG_RIGHT_CLUSTER][1] = set([(22, 17), (23, 17), (24, 17), (22, 16), (23, 16), (24, 16), (25, 16), (22, 15), (23, 15), (24, 15), (25, 15), (26, 15), (23, 14), (24, 14), (25, 14), (26, 14), (27, 14)])
		filter_bank[STRONG_RIGHT_CLUSTER][-1] = set([(14, 27), (14, 26), (15, 26), (14, 25), (15, 25), (16, 25), (15, 24), (16, 24), (17, 24), (16, 23), (17, 23), (18, 23), (17, 22), (18, 22), (19, 22), (18, 21), (19, 21), (20, 21), (19, 20), (20, 20), (21, 20), (20, 19), (21, 19), (22, 19)])

		filter_bank[WEAK_LEFT_CLUSTER][1] = set([(0, 14), (1, 14), (2, 14), (3, 14)])
		filter_bank[WEAK_LEFT_CLUSTER][-1] = set([(2, 16), (1, 15), (2, 15)])

		filter_bank[WEAK_RIGHT_CLUSTER][1] = set([(24, 14), (25, 14), (26, 14), (27, 14)])
		filter_bank[WEAK_RIGHT_CLUSTER][-1] = set([(25, 16), (25, 15), (26, 15)])

		return filter_bank
		
		





	def get_all_enemy_structures(self, game_state):

		structure_set = set()

		for x in range(0, 14):
			for y in range(14, 14 + x):
				unit = game_state.contains_stationary_unit([x,y])
				if unit:
					structure_set.add((x, y))

		for x in range(14, 28):
			for y in range(14, 41 - x):
				unit = game_state.contains_stationary_unit([x,y])
				if unit:
					structure_set.add((x, y))

		return structure_set






	def filter_blocked_locations(self, locations, game_state):
		filtered = []
		for location in locations:
			if not game_state.contains_stationary_unit(location):
				filtered.append(location)
		return filtered





	# TODO figure out how they attack and record the information
	def on_action_frame(self, turn_string):
		"""
		This is the action frame of the game. This function could be called 
		hundreds of times per turn and could slow the algo down so avoid putting slow code here.
		Processing the action frames is complicated so we only suggest it if you have time and experience.
		Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
		"""
		# Let's record at what position we get scored on
		state = json.loads(turn_string)
		events = state["events"]
		breaches = events["breach"]
		for breach in breaches:
			location = breach[0]
			unit_owner_self = True if breach[4] == 1 else False
			# When parsing the frame data directly, 
			# 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
			if not unit_owner_self:
				# gamelib.debug_write("Got scored on at: {}".format(location))
				self.scored_on_locations.append(location)
				# gamelib.debug_write("All locations: {}".format(self.scored_on_locations))
	




	def respawn_walls(self, game_state, wall_pos=[], low_health=True):
		# get all locations on my side of map
		
		if low_health:

			walls = []

			if not wall_pos:
				for x in range(0, 28):
					for y in range(13 - x, 13+1):
						unit = game_state.contains_stationary_unit([x,y])
						if unit:
							if unit.unit_type == WALL: # check unit type
								walls.append(([unit.x, unit.y],unit.health))

			else:
				for x, y in wall_pos:
					unit = game_state.contains_stationary_unit([x,y])
					if unit:
						if unit.unit_type == WALL: # check unit type
							walls.append(([x,y],unit.health))
					else:
						walls.append(([x,y],-1.0))
						# just try spawn
			walls.sort(key=lambda a : a[1])

			wall_cost = game_state.type_cost(WALL)

			for pos, health in walls:
				game_state.attempt_remove(pos)
				game_state.attempt_spawn(WALL, pos)

		else:
			for pos in wall_pos:
				game_state.attempt_remove(pos)
				game_state.attempt_spawn(WALL, pos)





if __name__ == "__main__":
	algo = AlgoStrategy()
	algo.start()
