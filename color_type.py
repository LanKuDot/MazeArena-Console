from enum import Enum, auto

class ColorType(Enum):
	"""The representation of colors in the maze arena

	@var NOT_DEFINED The color that haven't be defined yet
	@var MAZEC_CAR_TEAM_A The color that marks the maze cars of one team
	@var MAZEC_CAR_TEAM_B The color that marks the maze cars of another team
	"""
	NOT_DEFINED = auto()
	MAZE_CAR_TEAM_A = auto()
	MAZE_CAR_TEAM_B = auto()

	def __str__(self):
		"""The string represenation of each value
		"""
		return {
			self.NOT_DEFINED: "未指定",
			self.MAZE_CAR_TEAM_A: "隊伍 A",
			self.MAZE_CAR_TEAM_B: "隊伍 B"
		}.get(self)

class PosFinderType(Enum):
	"""An enum defines different types of PositionFinder

	@sa ColorPosManager.set_color()
	"""

	CAR_TEAM_A = auto()	
	CAR_TEAM_B = auto()

	@staticmethod
	def get_finder_type(color_type: ColorType):
		"""Get the ColorPosFinderType by ColorType

		The mapping of ColorType to the ColorPosFinderType:
		* MAZE_CAR_TEAM_A -> CAR_TEAM_A
		* MAZE_CAR_TEAM_B -> CAR_TEAM_B
		"""
		return {
			ColorType.MAZE_CAR_TEAM_A: PosFinderType.CAR_TEAM_A,
			ColorType.MAZE_CAR_TEAM_B: PosFinderType.CAR_TEAM_B
		}.get(color_type)
