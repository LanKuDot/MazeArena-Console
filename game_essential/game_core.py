"""The essential functions in the game.
"""

from enum import Enum, auto

import communication_server as comm_server
from .player_info_table import BasicPlayerInfoTable
from maze_manager import MazeManager, MazePositionFinder

class TeamType(Enum):
	A = auto()
	B = auto()

	def __str__(self):
		return {
			self.A: "A",
			self.B: "B"
		}.get(self)

class BasicTeamInfo:
	def __init__(self):
		self.team_type = None
		self.team_name = ""
		self.maze_pos_finder = None
		self.player_info_table = None

class BasicGameCore:
	def __init__(self, maze_manager: MazeManager, \
		player_info_table_T = BasicPlayerInfoTable, \
		team_info_T = BasicTeamInfo):

		self._player_info_table_T = player_info_table_T
		self._teams = {
			TeamType.A: team_info_T(),
			TeamType.B: team_info_T()
		}
		self._teammates = {}
		self._maze_manager = maze_manager
		self._comm_server = comm_server

		self._is_game_started = False

		self._set_handler()
		self._team_init()

	@property
	def is_game_started(self):
		return self._is_game_started

	def _set_handler(self):
		self._comm_server.set_disconnection_handler(self.player_quit)
		self._comm_server.add_command_handler("join", self.player_join)

	def _team_init(self):
		for team_type, team_info in self._teams.items():
			team_info.team_type = team_type
			team_info.maze_pos_finder = \
				self._maze_manager._get_finder_by_team_name(team_type.__str__())
			team_info.player_info_table = \
				self._player_info_table_T()

	def team_set_name(self, team_type: TeamType, team_name):
		self._teams[team_type].team_name = team_name

	def team_get_type_by_name(self, team_name) -> TeamType:
		for team_info in self._teams.values():
			if team_info.team_name is team_name:
				return team_info.team_type

	def player_join(self, player_ip, *args):
		"""The callback function when a player sends join command

		The command is: "join <player ID> <team name>".

		The method will try to find the player's team and
		create a new player info for that player in his team.
		The BasicGameCore._teammates will record the player's team.

		@param player_ip Specify the IP of the player
		@param args Specify a tuple (player ID, team name)
		"""
		team_type = self.team_get_type_by_name(args[1])
		player_info_table = self._teams[team_type].player_info_table
		player_info_table.add_player_info(player_ip, args[0])

		self._teammates[player_ip] = team_type

	def player_quit(self, player_ip):
		for team_info in self._teams.values():
			# If the player_ip is not in that table,
			# it will do nothing.
			team_info.player_info_table.delete_player_info(player_ip)

	def player_set_color(self, player_ip, color_bgr):
		for team_info in self._teams.values():
			# If the player_ip is not in that table,
			# it will do nothing.
			team_info.player_info_table.set_player_color(player_ip, color_bgr)

	def game_start(self):
		if self._is_game_started:
			return

		self._comm_server.boardcast_message("server game-start")
		self._is_game_started = True

	def game_stop(self):
		if not self._is_game_started:
			return

		self._comm_server.boardcast_message("server game-stop")
		self._is_game_started = False
