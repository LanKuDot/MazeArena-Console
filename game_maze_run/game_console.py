"""The console of the game: maze run

This game module is used to demonstrate the usage of package
game_essential. It only returns the position of the maze car
in the maze if it requests.
"""

from .game_core import GameCore, PlayerInfo, TeamType
from .widget_timer import TimerWidget
from game_essential import BasicPlayerInfoWidget, BasicTeamPanelWidget
from maze_manager import MazeManager
from tkinter import *
import logging

_logger = logging.getLogger(__name__)

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
		self._setup_handler_from_gamecore()

	def _setup_layout(self):
		control_panel = Frame(self, name = "control_panel")
		control_panel.pack(fill = X)
		btn_game_toggle = Button(control_panel, text = "遊戲開始", \
			command = self._toggle_game, name = "btn_game_toggle")
		btn_game_toggle.pack(side = LEFT)
		timer = TimerWidget(control_panel, self._game_stop_from_timer, name = "timer")
		timer.pack(side = LEFT, padx = 10)

		self._team_A_panel = TeamPanelWidget(self, "team A", TeamType.A, \
			self._game_core.team_set_name)
		self._team_A_panel.pack(fill = X, anchor = W)

	def _setup_handler_from_gamecore(self):
		self._game_core._handlers["player-join"] += self._add_player_widget
		self._game_core._handlers["player-quit"] += self._delete_player_widget
		self._game_core._handlers["game-stop"] += self._game_stop_from_gamecore

	def _add_player_widget(self, new_player_info: PlayerInfo, team_type: TeamType):
		if team_type is TeamType.A:
			team_car_pos = self._maze_manager.get_team_maze_pos(team_type.__str__())
			team_color = []
			for car_pos in team_car_pos:
				team_color.append(car_pos.color_bgr.__str__())
			self._team_A_panel.add_player(new_player_info, team_color, \
				self._game_core.player_kick)

	def _delete_player_widget(self, player_info: PlayerInfo, team_type: TeamType):
		if team_type is TeamType.A:
			self._team_A_panel.delete_player(player_info)

	def _toggle_game(self):
		_logger.debug("Toggle game button is pressed.")

		if not self._game_core.is_game_started:
			self._game_start_from_gm()
		else:
			self._game_stop_from_gm()

	def _game_start_from_gm(self):
		self.children["control_panel"].children["timer"].timer_start()
		self.children["control_panel"].children["btn_game_toggle"].config(text = "遊戲停止")
		self._game_core.game_start()

	# TODO Optimize these game-stop from different source
	def _game_stop_from_gm(self):
		self.children["control_panel"].children["timer"].timer_stop()
		self.children["control_panel"].children["btn_game_toggle"].config(text = "遊戲開始")
		self._game_core.game_stop()

	def _game_stop_from_gamecore(self):
		self.children["control_panel"].children["timer"].timer_stop()
		self.children["control_panel"].children["btn_game_toggle"].config(text = "遊戲開始")

	def _game_stop_from_timer(self):
		self.children["control_panel"].children["btn_game_toggle"].config(text = "遊戲開始")
		self._game_core.game_stop()
