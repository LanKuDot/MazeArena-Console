"""The essential functions in the game.
"""

import communication_server as comm_server
from .player_info_table import BasicPlayerInfoTable
from maze_manager import MazeManager

class BasicGameCore:
	def __init__(self, player_info_table: BasicPlayerInfoTable, \
		maze_manager: MazeManager):
		self._player_info_table = player_info_table
		self._maze_manager = maze_manager
		self._comm_server = comm_server

		self._is_game_started = False

	@property
	def is_game_started(self):
		return self._is_game_started

	def register_command(self):
		self._comm_server.set_disconnection_handler(self.player_quit)
		self._comm_server.add_command_handler("join", self.player_join)

	def player_join(self, player_ip, *args):
		self._player_info_table.add_player_info(player_ip, *args)

	def player_quit(self, player_ip):
		self._player_info_table.delete_player_info(player_ip)

	def player_set_color(self, player_ip, color_bgr):
		self._player_info_table.set_player_color(player_ip, color_bgr)

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
