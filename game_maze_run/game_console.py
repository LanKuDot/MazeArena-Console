"""The console of the game: maze run

This game module is used to demonstrate the usage of package
game_essential. It only returns the position of the maze car
in the maze if it requests.
"""

from .game_core import GameCore, PlayerInfo, TeamType
from game_essential import GameToggleButton, BasicPlayerInfoWidget, BasicTeamPanelWidget
from maze_manager import MazeManager
from tkinter import *

class PlayerInfoWidget(BasicPlayerInfoWidget):
	def __init__(self, master, player_info: PlayerInfo, color_list, **options):
		super().__init__(master, player_info, color_list, **options)

class TeamPanelWidget(BasicTeamPanelWidget):
	def __init__(self, master, team_title, team_type, fn_update_team_name, **options):
		super().__init__(master, team_title, team_type, fn_update_team_name, \
			PlayerInfoWidget, **options)

class GameConsoleWidget(LabelFrame):
	def __init__(self, master, game_core: GameCore, \
		maze_manager: MazeManager, **options):
		super().__init__(master, text = "遊戲控制", **options)
		self.pack()

		self._game_core = game_core
		self._maze_manager = maze_manager
		self._team_A_panel = None

		self._setup_layout()
		self._setup_handler_to_gamecore()

	def _setup_layout(self):
		control_panel = Frame(self)
		control_panel.pack(fill = X)
		btn_game_toggle = GameToggleButton(control_panel, self._game_core)
		btn_game_toggle.pack(side = LEFT)

		self._team_A_panel = TeamPanelWidget(self, "team A", TeamType.A, \
			self._game_core.team_set_name)
		self._team_A_panel.pack(fill = X, anchor = W)

	def _setup_handler_to_gamecore(self):
		self._game_core._handlers["player-join"] += self._add_player_widget
		self._game_core._handlers["player-quit"] += self._delete_player_widget

	def _add_player_widget(self, new_player_info: PlayerInfo, team_type: TeamType):
		if team_type is TeamType.A:
			team_car_pos = self._maze_manager.get_team_car_pos("A")
			team_color = []
			for car_pos in team_car_pos:
				team_color.append(car_pos.color_bgr.__str__())
			self._team_A_panel.add_player(new_player_info, team_color)

	def _delete_player_widget(self, player_info: PlayerInfo, team_type: TeamType):
		if team_type is TeamType.A:
			self._team_A_panel.delete_player(player_info)
