from xml.dom.minidom import parseString
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

		self.repair_list = []



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
			self.opening_game_strategy(game_state)

		elif game_state.turn_number == self.opening_phase:
			self.opening_game_strategy(game_state)
			self.clear_opening_game(game_state)

		elif game_state.turn_number < self.mid_phase:
			self.early_game_stratety(game_state)
			
		else:
			self.mid_game_strategy(game_state)

		# Submit the moves to terminal
		game_state.submit_turn()





	def opening_game_strategy(self, game_state):

		opening_wall_locations = [[0, 13], [1, 13], [26, 13], [27, 13], [2, 13], [3, 13], [4, 13], 
			[23, 13], [24, 13], [25, 13], [5, 12], [8, 12], [12, 12], [15, 12], [19, 12], [22, 12]]
		game_state.attempt_spawn(WALL, opening_wall_locations)
		
		corner_turret_locations = [[4, 12], [23, 12]]
		game_state.attempt_spawn(TURRET, corner_turret_locations)

		interceptor_deploy_locations = [[5, 8], [22, 8]]
		game_state.attempt_spawn(INTERCEPTOR, interceptor_deploy_locations)

		central_turret_locations = [[8, 11], [12, 11], [15, 11], [19, 11], [3, 12], [24, 12]]
		game_state.attempt_spawn(TURRET, central_turret_locations)

		additional_wall_locations = [[9, 12], [18, 12]]
		game_state.attempt_spawn(WALL, additional_wall_locations)

		additional_turret_locations = [[9, 11], [18, 11]]
		game_state.attempt_spawn(TURRET, additional_turret_locations)





	def mid_game_strategy(self, game_state):

		attack_MP_threshold = 12 + (game_state.turn_number // 14)
		attack_SP_threshold = 9 - (game_state.turn_number // 20)
		PICKUP_AMOUNT = self.get_pickup_refund(game_state)

		# TODO: FIX THIS LOCATIONS
		self.build_permanent_defense(game_state)

		if self.attack_state == DEFEND: 
			self.build_temporary_defense(game_state, True)
			self.mid_game_turtly(game_state)

			SUFFICIENT_MP = game_state.get_resource(MP) > attack_MP_threshold
			SUFFICIENT_SP = (game_state.get_resource(SP) + PICKUP_AMOUNT + 5) > attack_SP_threshold
			SUPPORT_SPAWNED = self.check_support_spawned(game_state)

			# TODO: ONLY GO INTO PREPPY IF THERE ARE ENOUGH WALLS TO FUND AN ATTACK
			if SUFFICIENT_SP and SUFFICIENT_MP:
				self.mid_game_preppy(game_state)

		else:
			# kamikaze
			self.mid_game_kamikazy(game_state)




	# def mid_game_zelensky(self, game_state): 
	# 	# Spawn Priority: 
		
	# 	# PINK = long wall/turrets
	# 	pink_wall_locations = [[10, 12], [11, 12], [12, 12], [13, 12], [14, 12], 
	# 							[15, 12], [16, 12], [17, 12], [18, 12], [19, 12], 
	# 							[20, 12], [21, 12], [22, 12], [4, 11], [5, 10]]
	# 	pink_turret_locations = [[6, 10], [8, 10]]
	# 	game_state.attempt_spawn(WALL, pink_wall_locations)
	# 	game_state.attempt_spawn(TURRET, pink_turret_locations)

	# 	# YELLOW = extra wall length/ turret / support 
	# 	yellow_wall_locations = [[7, 12], [8, 12], [9, 12]]
	# 	yellow_turret_locations = [[9, 10], [10, 10], [12, 10], [13, 10], [18, 10], [22, 10]]
	# 	yellow_support_locations = [[14, 9], [15, 9], [17, 9], [19, 9]]

	# 	game_state.attempt_spawn(WALL, yellow_wall_locations)
	# 	self.build_permanent_defense(game_state, upgrade=True)

	# 	game_state.attempt_spawn(TURRET, yellow_turret_locations)
	# 	game_state.attempt_spawn(SUPPORT, yellow_support_locations)
		
	# 	# ORANGE = extra turret + extra support 
	# 	orange_turret_locations = [[14, 10], [15, 10], [17, 10], [19, 10]]
	# 	orange_support_locations = [[23, 11], [18, 9], [18, 8], [19, 8]]

	# 	game_state.attempt_upgrade(pink_turret_locations)
	# 	game_state.attempt_upgrade(pink_wall_locations)

	# 	game_state.attempt_spawn(TURRET, orange_turret_locations)
	# 	game_state.attempt_spawn(SUPPORT, orange_support_locations)

	# 	game_state.attempt_upgrade(yellow_support_locations)
	# 	game_state.attempt_upgrade(yellow_wall_locations)
	# 	game_state.attempt_upgrade(yellow_turret_locations)

	# 	game_state.attempt_upgrade(orange_support_locations)
	# 	game_state.attempt_upgrade(orange_turret_locations)




	def early_game_stratety(self, game_state):
		# Spawn Priority:
		# TODO: place_mid_defense -> add in more turrets in corner 	
		# 8 upgrade outside pinks 
		pink_turret_locations = [[12, 10], [15, 10], [8, 10], [19, 10]]
		pink_wall_locations = [[8, 11], [12, 11], [15, 11], [19, 11], [9, 11], 
			[10, 11], [11, 11], [16, 11], [17, 11], [18, 11]]

		teal_turret_locations = [[5, 11], [22, 11]]
		teal_wall_locations = [[6, 11], [7, 11], [20, 11], [21, 11], [13, 11], [14, 11]]
		
		# 24 points in pink 
		game_state.attempt_spawn(WALL, pink_wall_locations)
		game_state.attempt_spawn(TURRET, pink_turret_locations)

		# 4 turrets to put in green 
		game_state.attempt_spawn(WALL, teal_wall_locations)
		game_state.attempt_spawn(TURRET, teal_turret_locations)

		# upgrades corner walls/ turrets 
		self.build_permanent_defense(game_state)
		self.build_temporary_defense(game_state)

		game_state.attempt_upgrade([[12, 10], [15, 10]])

		self.build_permanent_defense(game_state, True)
		self.build_temporary_defense(game_state, True)

		game_state.attempt_spawn(INTERCEPTOR, [[16,2], [11,2]])
		




	def mid_game_turtly(self, game_state):

		## TODO 1.) Upgrade turrets before upgrading walls 
		## 2.) corner turrets, center turrets, then others for upgrading 
		## 3.) make sure all turrets have corner walls 

		# TODO: place_mid_defense -> add in more turrets in corner 	

		# 8 upgrade outside pinks 
		pink_peri_wall = [[6, 11], [20, 11], [7, 11], [21, 11], [5, 13], [23, 13]]
		pink_center_wall = [[8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], [15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [5, 12], [22, 12]]
		
		mid_turret_locations = [[15, 10], [12, 10]]
		peri_turret_locations = [[8, 10], [19, 10]]
		side_turret_locations = [[4,12], [24, 12], [3, 12], [24,12]]
		flank_turret_locations = [[5, 11], [22, 11], [10, 10], [17, 10], [4, 11], [23, 11]]
		extra_turret_locations = [[2, 12], [25, 12], [1, 12], [26, 12]]
		
		support_base_turret_locations = [[12,5], [15,5]]
		turret_locations = mid_turret_locations + peri_turret_locations + side_turret_locations + flank_turret_locations + extra_turret_locations + support_base_turret_locations
		yellow_wall_locations = [[6, 10], [7, 10], [9, 10], [11, 10], [13, 10], [14, 10], [16, 10], [18, 10], [20, 10], [21, 10], [5, 10], [22, 10]]
		base_support_locations = [[13, 2], [14, 2]]
		extra_support_locations = [[13, 4], [13, 3], [14, 3], [14, 4]]

		# spawns the turrets that were removed for repair
		if self.repair_list:
			game_state.attempt_spawn(TURRET, self.repair_list)
			self.repair_list = []
		
		# spawns turrets in the center line
		game_state.attempt_spawn(TURRET, mid_turret_locations)
		game_state.attempt_spawn(TURRET, peri_turret_locations)

		# spawns main wall
		game_state.attempt_spawn(WALL, pink_center_wall)
		
		# upgrades corner walls/ turrets 
		self.build_permanent_defense(game_state, True)
		
		# upgrade corner turrets
		game_state.attempt_upgrade(side_turret_locations)

		# upgrade 2 center turrets
		game_state.attempt_upgrade(mid_turret_locations)

		# spawn two turrets on the peripheries
		game_state.attempt_spawn(TURRET, extra_turret_locations)
		game_state.attempt_spawn(TURRET, flank_turret_locations)

		game_state.attempt_upgrade(extra_turret_locations)
		game_state.attempt_upgrade(flank_turret_locations)
		
		# upgrade peri turrets
		game_state.attempt_upgrade(peri_turret_locations)
		# add in two more wall units in the main line per side
		game_state.attempt_spawn(WALL, pink_peri_wall)

		# spawn wall between turrets behind main line 
		game_state.attempt_spawn(WALL, yellow_wall_locations)
	
		game_state.attempt_spawn(SUPPORT, base_support_locations)
				
		if game_state.get_resource(SP) > 5:
			game_state.attempt_upgrade(pink_center_wall)
			game_state.attempt_upgrade(pink_peri_wall)

		## REPAIR METHOD: If turrets fall below 50% of max health, then remove and put down again 
		## what should the priorities be for this/?
		for location in turret_locations:
			turret = game_state.contains_stationary_unit(location)
			if turret and turret.health < 0.3 * turret.max_health: 
				self.repair_list.append(location)
				game_state.attempt_remove(location)
			
	
		game_state.attempt_spawn(SUPPORT, extra_support_locations)

		game_state.attempt_spawn(TURRET, support_base_turret_locations)

		game_state.attempt_upgrade(base_support_locations)

		game_state.attempt_upgrade(pink_peri_wall)
		game_state.attempt_upgrade(extra_support_locations)

		game_state.attempt_spawn(TURRET, extra_turret_locations)
		game_state.attempt_upgrade(extra_turret_locations)

		# spawn interceptors if gap in wall
		# check spawn points

		left_corner_structs = [[0, 13], [1, 13], [2, 13], [3, 13], [3, 12]]
		left_flank_structs = [[4, 13], [4, 12], [5, 12], [5, 11], [6, 11]]
		left_main_structs = [[7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [8, 10]]
		central_main_structs = [[12, 11], [13, 11], [14, 11], [15, 11], [12, 10], [15, 10]]
		right_main_structs = [[16, 11], [17, 11], [18, 11], [19, 11], [20, 11], [19, 10]]
		right_flank_structs = [[23, 13], [22, 12], [23, 12], [21, 11], [22, 11]]
		right_corner_structs = [[24, 13], [25, 13], [26, 13], [27, 13], [24, 12]]

		left_corner_count = 0
		left_flank_count = 0
		left_main_count = 0
		central_main_count = 0
		right_main_count = 0
		right_flank_count = 0
		right_corner_count = 0

		for location in left_corner_structs:
			if game_state.contains_stationary_unit(location):
				left_corner_count += 1

		for location in left_flank_structs:
			if game_state.contains_stationary_unit(location):
				left_flank_count += 1

		for location in left_main_structs:
			if game_state.contains_stationary_unit(location):
				left_main_count += 1

		for location in central_main_structs:
			if game_state.contains_stationary_unit(location):
				central_main_count += 1

		for location in right_main_structs:
			if game_state.contains_stationary_unit(location):
				right_main_count += 1

		for location in right_flank_structs:
			if game_state.contains_stationary_unit(location):
				right_flank_count += 1

		for location in right_corner_structs:
			if game_state.contains_stationary_unit(location):
				right_corner_count += 1


		num_spawned = game_state.turn_number // 30

		if left_corner_count <= 3:
			game_state.attempt_spawn(INTERCEPTOR, [2,11], num_spawned)

		if left_flank_count <= 3 or ((left_corner_count + left_flank_count) <= 7):
			game_state.attempt_spawn(INTERCEPTOR, [4,9], num_spawned)

		if left_main_count <= 4:
			game_state.attempt_spawn(INTERCEPTOR, [7,6], num_spawned)

		if central_main_count <= 5:
			game_state.attempt_spawn(INTERCEPTOR, [[7,6], [20, 6]])

		if right_main_count <= 4:
			game_state.attempt_spawn(INTERCEPTOR, [20,6], num_spawned)

		if right_flank_count <= 3 or ((right_corner_count + right_flank_count) <= 7):
			game_state.attempt_spawn(INTERCEPTOR, [23,9], num_spawned)

		if right_corner_count <= 3:
			game_state.attempt_spawn(INTERCEPTOR, [25,11], num_spawned)


		if self.get_pickup_refund(game_state) < 5:
			game_state.attempt_spawn(INTERCEPTOR, [13, 0])





	# TODO: MAKE THIS SIDE SPECIFIC
	def get_pickup_refund(self, game_state):
		yellow_wall_locations = [[6, 10], [7, 10], [9, 10], [10, 10], [11, 10], 
				[13, 10], [14, 10], [16, 10], [17, 10], [18, 10], [20, 10], [21, 10]]
		
		refund = 0
		for location in yellow_wall_locations:
			struct = game_state.contains_stationary_unit(location)
			if struct:
				refund += 1
		
		return refund


	def check_support_spawned(self, game_state):
		base_support_locations = [[13, 2], [14, 2]]

		for location in base_support_locations:
			struct = game_state.contains_stationary_unit(location)
			if struct:
				return True
			else:
				return False



	def mid_game_preppy(self, game_state): 
		
		self.determine_kamikaze_side(game_state)

		# TODO: PICK THE BETTER SIDE
		# prepare
		yellow_wall_locations = [[6, 10], [7, 10], [9, 10], [10, 10], [11, 10], 
			[13, 10], [14, 10], [16, 10], [17, 10], [18, 10], [20, 10], [21, 10]]
		temp_left_wall_locations = [[0, 13],[1, 13],[1, 12], [2, 12], [3, 12], [4, 11]]
		temp_right_wall_locations = [[26, 13], [27, 13],[26, 12], [25, 12]]

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
		

		# TODO: if this damage is below some threshold, we can send interceptors, scoring much higher
		if left_damage < right_damage:
			self.attack_state = LEFT_KAMIKAZE
		else:
			self_attack_state = RIGHT_KAMIKAZE





	def mid_game_kamikazy(self, game_state):
		
		req_points = 10
		num_sups = 0

		back_channel_wall = [[13, 2], [14, 2]]
		interior_channel_wall_left = [[15, 3], [16, 3]]
		interior_channel_wall_right = [[11, 3], [12, 3]]

		attack_channel_wall_left = [[5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3]]
		attack_front_wall_left = [[4, 11], [3, 12], [2, 13]]

		attack_channel_wall_right = [[15, 3], [16, 4], [17, 5], [18, 6], [19, 7], [20, 8], [21, 9], [22, 10], [23, 11], [24, 12], [25, 13]]

		left_kamikaze_wall = [[1, 14], [2, 14]]
		right_kamikaze_wall = [[25, 14], [26, 14]]

		attack_spawn_locs_left = []
		attack_spawn_locs_right = []


		to_kamikaze = True

		for location in left_kamikaze_wall:
			if game_state.contains_stationary_unit(location):
				pass
			else:
				to_kamikaze = False


		if not to_kamikaze and (not game_state.contains_stationary_unit([0, 14]) or not game_state.contains_stationary_unit([1, 15])):
			to_kamikaze = True

		# TODO: add switching based on self.attack_state == LEFT_KAMIKAZE or self.attack_state == RIGHT_KAMIKAZE
		
		game_state.attempt_spawn(WALL, interior_channel_wall_left)

		if to_kamikaze:

			game_state.attempt_spawn(WALL, back_channel_wall)
			game_state.attempt_spawn(WALL, attack_front_wall_left)
			
			for location in attack_channel_wall_left:
				if game_state.get_resource(SP) > req_points + 2:
					game_state.attempt_spawn(SUPPORT, location)
					num_sups += 1
				else:
					game_state.attempt_spawn(WALL, location)
				req_points -= 1

		else:
			# DESTRUCTOR ATTACK
			pink_peri_wall = [[6, 11], [20, 11], [7, 11], [21, 11], [5, 13], [23, 13]]
			pink_center_wall = [[8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], [15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [5, 12], [22, 12]]
			game_state.attempt_spawn(WALL, pink_peri_wall)
			game_state.attempt_spawn(WALL, pink_center_wall)
			game_state.attempt_spawn(SUPPORT, back_channel_wall)
			game_state.attempt_spawn(SUPPORT, attack_channel_wall_left)
			game_state.attempt_spawn(SUPPORT, attack_front_wall_left)
		
		game_state.attempt_upgrade(attack_channel_wall_left)

		game_state.attempt_remove(interior_channel_wall_left)
		game_state.attempt_remove(attack_channel_wall_left)

		for location in back_channel_wall: 
			struct = game_state.contains_stationary_unit(location)
			if struct.unit_type == WALL: 
				game_state.attempt_remove(location)

		
		if to_kamikaze:
			game_state.attempt_spawn(SCOUT, [14, 0], int(12 - (num_sups // 2)))
			game_state.attempt_spawn(SCOUT, [14, 0], int(game_state.get_resource(MP) // 8))
			game_state.attempt_spawn(SCOUT, [16, 2], 1000)

		else:
			# DESTRUCTOR ATTACK
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




	def clear_opening_game(self, game_state):
		points_to_remove = [[6, 12], [7, 12], [8, 12], [9, 12], [10, 12], 
			[11, 12], [12, 12], [13, 12], [14, 12], [15, 12], [16, 12], [17, 12], 
			[18, 12], [19, 12], [20, 12], [21, 12], [6, 11], 
			[7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], 
			[15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [20, 11], [21, 11]]
		game_state.attempt_remove(points_to_remove)


	def clear_early_game(self, game_state):
		points_to_remove = [[8, 11], [12, 11], [15, 11], [19, 11], [9, 10], 
			[10, 10], [11, 10], [16, 10], [17, 10], [18, 10]]
		game_state.attempt_remove(points_to_remove)



if __name__ == "__main__":
	algo = AlgoStrategy()
	algo.start()
