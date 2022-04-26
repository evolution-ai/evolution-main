import gamelib
import random
import math
import warnings
from sys import maxsize
import json

class AlgoUtil():

	def __init__(self):
		pass

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