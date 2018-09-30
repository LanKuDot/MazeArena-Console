from enum import Enum, auto

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

	def __str__(self):
		"""The string represenation of each value
		"""
		return {
			self.NOT_DEFINED: "未指定",
			self.MAZE_UPPER_PLANE: "迷宮上平面",
			self.MAZE_LOWER_PLANE: "迷宮下平面",
			self.MAZE_CAR_TEAM_A: "隊伍 A",
			self.MAZE_CAR_TEAM_B: "隊伍 B"
		}.get(self)

class PosFinderType(Enum):
	"""An enum defines different types of PositionFinder

	It is similar to ColorType, but the MAZE_UPPER_PLANE and MAZE_LOWER_PLANE
	are both belongs to MAZE.

	@sa ColorPosManager.set_color()
	"""

	MAZE = auto()
	CAR_TEAM_A = auto()	
	CAR_TEAM_B = auto()

	@staticmethod
	def get_finder_type(color_type: ColorType):
		"""Get the ColorPosFinderType by ColorType

		The mapping of ColorType to the ColorPosFinderType:
		* MAZE_UPPER_PLANE -> MAZE
		* MAZE_LOWER_PLANE -> MAZE
		* MAZE_CAR_TEAM_A -> CAR_TEAM_A
		* MAZE_CAR_TEAM_B -> CAR_TEAM_B
		"""
		return {
			ColorType.MAZE_LOWER_PLANE: PosFinderType.MAZE,
			ColorType.MAZE_UPPER_PLANE: PosFinderType.MAZE,
			ColorType.MAZE_CAR_TEAM_A: PosFinderType.CAR_TEAM_A,
			ColorType.MAZE_CAR_TEAM_B: PosFinderType.CAR_TEAM_B
		}.get(color_type)
