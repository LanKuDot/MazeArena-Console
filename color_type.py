from enum import Enum

class ColorType(Enum):
	"""The representation of colors in the maze arena

	@var NOT_DEFINED enum = 0 The color that haven't be defined yet
	@var MAZE_UPPER_PLANE enum = 1 The color that marks the upper plane of the maze
	@var MAZE_LOWER_PLANE enum = 2 The color that marks the lower plane of the maze
	@var MAZEC_CAR_TEAM_A enum = 3 The color that marks the maze cars of one team
	@var MAZEC_CAR_TEAM_B enum = 4 The color that marks the maze cars of another team
	"""
	NOT_DEFINED = 0
	MAZE_UPPER_PLANE = 1
	MAZE_LOWER_PLANE = 2
	MAZE_CAR_TEAM_A = 3
	MAZE_CAR_TEAM_B = 4
