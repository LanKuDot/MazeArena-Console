"""The console of the game: run and catch
"""

from .game_core import GameCore, PlayerInfo, TeamType
from .widget_timer import TimerWidget
from game_essential import BasicPlayerInfoWidget, BasicTeamPanelWidget
from maze_manager import MazeManager
from tkinter import *
import tkinter.font as font

class PlayerInfoWidget(BasicPlayerInfoWidget):
	def __init__(self, master, player_info: PlayerInfo, color_list, **options):
		super().__init__(master, player_info, color_list, **options)

	def set_label_color(self, color_name):
		self.children["color_label"].config(background = color_name)

class TeamPanelWidget(BasicTeamPanelWidget):
	def __init__(self, master, team_title, team_type, fn_update_team_name, **options):
		super().__init__(master, team_title, team_type, fn_update_team_name, \
			PlayerInfoWidget, **options)

	def add_player(self, player_info, color_list, label_color_name):
		super().add_player(player_info, color_list)
		self.set_player_color_label(player_info.IP, label_color_name)

	def set_player_color_label(self, player_ip, label_color_name):
		self._player_widgets[player_ip].set_label_color(label_color_name)

	def set_all_color_label(self, label_color_name):
		for player_ip in self._player_widgets.keys():
			self.set_player_color_label(player_ip, label_color_name)

class GameConsoleWidget(LabelFrame):
	def __init__(self, master, game_core: GameCore, \
		maze_manager: MazeManager, **options):
		super().__init__(master, text = "遊戲控制", **options)
		self.pack()

		self._game_core = game_core
		self._maze_manager = maze_manager
		self._team_catcher_panel = None
		self._team_runner_panel = None
		self._num_of_survivor = 0

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

		label_font = font.Font(family = "Microsoft JhengHei UI", \
			size = 15, weight = font.BOLD)

		info_panel = Frame(self, name = "info_panel")
		info_panel.pack()
		label_survivor_title = Label(info_panel, text = "存活數: ", font = label_font)
		label_survivor_title.pack(side = LEFT)
		label_num_of_survivor = Label(info_panel, text = "0", font = label_font, \
			name = "num_of_survivor")
		label_num_of_survivor.pack(side = LEFT)

		self._team_catcher_panel = TeamPanelWidget(self, "catchers - Team A", \
			GameCore.TEAM_CATCHER, self._game_core.team_set_name)
		self._team_catcher_panel.pack(fill = X, anchor = W)
		self._team_runner_panel = TeamPanelWidget(self, "runners - Team B", \
			GameCore.TEAM_RUNNER, self._game_core.team_set_name)
		self._team_runner_panel.pack(fill = X, anchor = W)

	def _setup_handler_from_gamecore(self):
		self._game_core._handlers["player-join"] += self._add_player_widget
		self._game_core._handlers["player-quit"] += self._delete_player_widget
		self._game_core._handlers["game-stop"] += self._game_stop_from_gamecore
		self._game_core._handlers["game-catched"] += self._runner_is_catched

	def _add_player_widget(self, new_player_info: PlayerInfo, team_type: TeamType):
		team_car_pos = self._maze_manager.get_team_car_pos(team_type.__str__())
		team_color = []
		for car_pos in team_car_pos:
			team_color.append(car_pos.color_bgr.__str__())

		if team_type is GameCore.TEAM_CATCHER:
			self._team_catcher_panel.add_player(new_player_info, team_color, "blue")
		else:
			self._team_runner_panel.add_player(new_player_info, team_color, "red")

	def _delete_player_widget(self, player_info: PlayerInfo, team_type: TeamType):
		if team_type is GameCore.TEAM_CATCHER:
			self._team_catcher_panel.delete_player(player_info)
		else:
			self._team_runner_panel.delete_player(player_info)

	def _runner_is_catched(self, player_ip):
		"""Set the color label of the runner to gray and update the number of survivor
		"""
		self._team_runner_panel.set_player_color_label(player_ip, "gray")

		self._num_of_survivor -= 1
		self.children["info_panel"].children["num_of_survivor"] \
			.config(text = self._num_of_survivor.__str__())

	def _toggle_game(self):
		if not self._game_core.is_game_started:
			self._game_start_from_gm()
		else:
			self._game_stop_from_gm()

	def _game_start_from_gm(self):
		"""Start the game

		Start the timer and the game core, and initialize the number of survivors.
		"""
		self.children["control_panel"].children["timer"].timer_start()
		self.children["control_panel"].children["btn_game_toggle"].config(text = "遊戲停止")

		self._num_of_survivor = self._team_runner_panel.num_of_player_widgets()
		self.children["info_panel"].children["num_of_survivor"] \
			.config(text = self._num_of_survivor.__str__())
		self._team_runner_panel.set_all_color_label("red")

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
