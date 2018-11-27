"""The game core of the game maze run
"""

from game_essential import BasicGameCore
from game_essential import BasicPlayerInfo, BasicTeamInfo, TeamType
from maze_manager import MazeManager

class PlayerInfo(BasicPlayerInfo):
	def __init__(self):
		super().__init__()

class TeamInfo(BasicTeamInfo):
	def __init__(self):
		super().__init__(PlayerInfo)

class GameCore(BasicGameCore):
	def __init__(self, maze_manager: MazeManager):
		super().__init__(maze_manager, TeamInfo)

	def _set_handler_to_server(self):
		super()._set_handler_to_server()
		self._comm_server.add_command_handler("game-touch", self.game_touch)

	@BasicGameCore.game_started
	def game_touch(self, player_ip):
		self.game_stop()
