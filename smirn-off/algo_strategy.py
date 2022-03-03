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
		
		if game_state.turn_number == 0:
			self.opening_strategy(game_state)

		elif game_state.turn_number < self.mid_phase:
			self.early_game_strategy(game_state)

		elif game_state.turn_number == self.mid_phase:
			self.early_game_strategy(game_state)
			self.clear_early_game(game_state)

		else:
			self.mid_game_strategy(game_state)
		game_state.submit_turn()







	def clear_early_game(game_state):
		points_to_remove = [[5, 12], [6, 12], [7, 12], [8, 12], [9, 12], [10, 12], [11, 12], [12, 12], 
				[13, 12], [14, 12], [15, 12], [16, 12], [17, 12], [18, 12], [19, 12], [20, 12], [21, 12], 
				[22, 12], [5, 11], [6, 11], [7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], 
				[14, 11], [15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [20, 11], [21, 11], [22, 11]]
		game_state.attempt_remove(points_to_remove)



	def mid_game_strategy(self, game_state):
		# TODO: attack, defend, prepare

		# MP < thresh -> defend
		# MP > thresh -> prepare
		# attack = 1 -> attack

		defend_threshold = 16

		# refer to that image for my bs names
		# TODO: FUNCTIONALISE THIS CODE FOR EASY READING
		if game_state.get_resource(MP) < defend_threshold:
			self.place_mid_game_defense(game_state)

		else:
			if not self.attack_state:

				self.place_mid_game_defense(game_state)

				# prepare
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
				

				# TODO: PICK THE BETTER SIDE
				temp_left_wall_locations = [[ 0, 13],[ 1, 13],[ 1, 12]]
				temp_right_wall_locations = [[ 26, 13],[ 27, 13],[ 26, 12]]

				game_state.attempt_remove(temp_left_wall_locations)

				if game_state.get_resource(SP) < 20:
					pink_walls_layer_two_locations = [[6, 10], [8, 10], [9, 10], [10, 10], [12, 10], [13, 10], [14, 10], [15, 10], [17, 10], [18, 10], [19, 10], [21, 10]]
					game_state.attempt_remove(pink_walls_layer_two_locations)

				self.attack_state = 1
			else:
				# ATTACK MFFFFF DIEEEE XD
				attack_channel_wall = [[5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3], [15, 3], [13, 2], [14, 2], [16, 3], [17, 3]]
				
				game_state.attempt_spawn(WALL, attack_channel_wall)
				game_state.attempt_remove(attack_channel_wall)

				game_state.attempt_spawn(SCOUT, [14, 0], 9)
				game_state.attempt_spawn(SCOUT, [16, 2], 1000)

				self.attack_state = 0




	

	def place_mid_game_defense(self, game_state):
		# spawn priority:

		# green stuff (outside this function)

		# blue wall (temp walls)

		# yellow wall
		# yellow turret

		# pink wall layer 1

		# upgrade yellow turrets

		# yellow permanent supports
		# pink wall layer 2

		# upgrade yellow walls
		# upgrade permanent support

		temp_wall_locations = [[ 0, 13],[ 1, 13],[ 26, 13],[ 27, 13],[ 1, 12],[ 26, 12]]
		game_state.attempt_spawn(WALL, temp_wall_locations)

		yellow_walls_locations = [[5, 13], [22, 13], [5, 12], [22, 12], [5, 11], [6, 11], [21, 11], [22, 11]]
		game_state.attempt_spawn(WALL, yellow_walls_locations)

		yellow_turrets_locations = [[7, 10], [11, 10], [16, 10], [20, 10]]
		game_state.attempt_spawn(TURRET, yellow_turrets_locations)

		# right now only one layer of pink
		pink_wall_locations = [[7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], [14, 11], [15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [20, 11], [6, 10], [8, 10], [9, 10], [10, 10], [12, 10], [13, 10], [14, 10], [15, 10], [17, 10], [18, 10], [19, 10], [21, 10]]
		game_state.attempt_spawn(WALL, pink_wall_locations)

		perm_turret_locations = [[ 3, 12],[ 4, 12],[ 23, 12],[ 24, 12]]
		game_state.attempt_upgrade(perm_turret_locations)

		game_state.attempt_upgrade(yellow_turrets_locations)

		yellow_support_locations = [[13, 4], [14, 4]]
		game_state.attempt_spawn(SUPPORT, yellow_support_locations)

		perm_wall_locations = [[ 2, 13],[ 3, 13],[ 4, 13],[ 23, 13],[ 24, 13],[ 25, 13]]
		game_state.attempt_upgrade(temp_wall_locations)
		game_state.attempt_upgrade(perm_wall_locations)
		
		game_state.attempt_upgrade(yellow_walls_locations)
		game_state.attempt_upgrade(yellow_support_locations)

		yellow_extra_support_locations = [[12, 5], [13, 5], [14, 5], [15, 5]]
		game_state.attempt_spawn(SUPPORT, yellow_extra_support_locations)

		game_state.attempt_upgrade(pink_wall_locations)
		game_state.attempt_upgrade(yellow_extra_support_locations)








	def build_perm_defences(self, game_state):
		"""
		Build basic defenses using hardcoded locations.
		Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
		"""
		# Place turrets that attack enemy units on the corners
		perm_turret_locations = [[ 3, 12],[ 4, 12],[ 23, 12],[ 24, 12]]

		# attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
		game_state.attempt_spawn(TURRET, perm_turret_locations)
		
		# Place walls in the corners to prevent attacks
		perm_wall_locations = [[ 2, 13],[ 3, 13],[ 4, 13],[ 23, 13],[ 24, 13],[ 25, 13]]
		game_state.attempt_spawn(WALL, perm_wall_locations)





	def early_game_strategy(self, game_state):
		"""
		Send out interceptors at random locations to defend our base from enemy moving units.
		"""
		# TODO: there has to be a better way
		# # We can spawn moving units on our edges so a list of all our edge locations
		# friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
		
		# # Remove locations that are blocked by our own structures 
		# # since we can't deploy units there.
		# deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
		
		deploy_locations = [[9, 4], [18, 4]]
		
		for location in deploy_locations:
			game_state.attempt_spawn(INTERCEPTOR, location)


		temp_wall_locations = [[ 0, 13],[ 1, 13],[ 26, 13],[ 27, 13]]
		game_state.attempt_spawn(WALL, temp_wall_locations)

		while game_state.get_resource(SP) >= 3:

			random_x = random.randint(6, 21)
			wall_location = [random_x, 12]
			turret_location = [random_x, 11]

			game_state.attempt_spawn(WALL, wall_location)
			game_state.attempt_spawn(TURRET, turret_location)
			
			# game_state.attempt_remove(wall_location)
			# game_state.attempt_remove(turret_location)
			


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
		return location_options[damages.index(min(damages))]


	def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
		total_units = 0
		for location in game_state.game_map:
			if game_state.contains_stationary_unit(location):
				for unit in game_state.game_map[location]:
					if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
						total_units += 1
		return total_units
		

	def filter_blocked_locations(self, locations, game_state):
		filtered = []
		for location in locations:
			if not game_state.contains_stationary_unit(location):
				filtered.append(location)
		return filtered


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
				gamelib.debug_write("Got scored on at: {}".format(location))
				self.scored_on_locations.append(location)
				gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
	algo = AlgoStrategy()
	algo.start()
