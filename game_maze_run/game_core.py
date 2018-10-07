"""The game core of the game maze run
"""

from game_essential import BasicGameCore
from game_essential import BasicPlayerInfoTable, BasicPlayerInfo
from game_essential import BasicTeamInfo, TeamType
from maze_manager import MazeManager

class PlayerInfo(BasicPlayerInfo):
	def __init__(self):
		super().__init__()

class PlayerInfoTable(BasicPlayerInfoTable):
	def __init__(self):
		super().__init__(PlayerInfo)

class TeamInfo(BasicTeamInfo):
	def __init__(self):
		super().__init__()

class GameCore(BasicGameCore):
	def __init__(self, maze_manager: MazeManager):
		super().__init__(maze_manager, PlayerInfoTable, TeamInfo)
