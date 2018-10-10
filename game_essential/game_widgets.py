"""The widget that would be used in the game
"""

from tkinter import *
import tkinter as tk
from .game_core import BasicGameCore
from .player_info import BasicPlayerInfo

class GameToggleButton(Button):
	"""The button that makes game start or stop

	@vat _game_core The GameCore object to be toggled
	"""

	def __init__(self, master, game_core: BasicGameCore, **options):
		super().__init__(master, text = "遊戲開始", \
			command = self._toggle_game, **options)
		self.pack()

		self._game_core = game_core

	def _toggle_game(self):
		if not self._game_core.is_game_started:
			self.game_start()
		else:
			self.game_stop()

	def game_start(self):
		self._game_core.game_start()
		self.config(text = "遊戲停止")

	def game_stop(self):
		self._game_core.game_stop()
		self.config(text = "遊戲開始")

class BasicPlayerInfoWidget(Frame):
	"""The widget for setting and displaying PlayerInfo

	Usage:
	```
	playerInfoWidget = PlayerInfoWidget(...)
	playerInfoWidget.pack()

	playerInfoWidget.refresh() # To reflect the changes in PlayerInfo
	```

	@var _player_info The PlayerInfo object this widget binds
	@var _selected_color_bgr The trace variable of the color selection
	     in the OptionMenu
	@var _previous_selected_color_bgr The color selected at previous time
	"""

	def __init__(self, master, player_info: BasicPlayerInfo, color_list, \
		**options):
		"""Constructor

		@param master The parent widget
		@param player_info The target player information to be shwon
		@param color_list The selectable color for this player.
		       It will be a list of string representation of the color_bgr,
		       such as ["[123, 123, 123]", "[100, 100, 100]"]
		@param option Other options for Frame widget
		"""
		super().__init__(master, **options)
		self.pack()

		self._player_info = player_info
		self._selected_color_bgr = StringVar(self, "顏色未定")
		self._selected_color_bgr.trace("w", self._update_player_color)
		self._previous_selected_color_bgr = self._selected_color_bgr.get()

		self._setup_layout(color_list)

	def _setup_layout(self, color_list):
		"""Set up the layout of the widget

		It will be like:
		+-------------------------+
		| [] IP ID [Color +] |
		+-------------------------+

		@param color_list Specify the selectable color list in string
		"""
		color_label = Label(self, background = "gray", \
			width = 1, name = "color_label")
		color_label.pack(side = LEFT)
		spacer = Label(self, width = 1)
		spacer.pack(side = LEFT)
		ip = Label(self, text = self._player_info.IP, \
			width = 14, anchor = W, name = "ip")
		ip.pack(side = LEFT)
		id = Label(self, text = "-", \
			width = 8, anchor = W, name = "id")
		id.pack(side = LEFT)
		color_menu = OptionMenu(self, self._selected_color_bgr, \
			*color_list)
		color_menu.configure(width = 13)
		color_menu.pack(side = LEFT)

	def _update_player_color(self, *args):
		"""Update the selected color into PlayerInfo.color_bgr
		"""
		color_bgr_str = self._selected_color_bgr.get()
		if color_bgr_str == "顏色未定" or \
			color_bgr_str == self._previous_selected_color_bgr:
			return

		self._previous_selected_color_bgr = color_bgr_str
		# Convert the string into the list it represents (like reversed __str__)
		# color_bgr_str will be "[123,123,123]"
		color_bgr_str = color_bgr_str.strip("[]").split(",")
		color_bgr = []
		for color in color_bgr_str:
			color_bgr.append(int(color))
		self._player_info.color_bgr = color_bgr

	def refresh(self):
		"""Make the widget refresh the displaying information
		"""
		ip_text = self._player_info.IP if self._player_info.IP else "-"
		self.children["ip"].config(text = ip_text)
		id_text = self._player_info.ID if self._player_info.ID else "-"
		self.children["id"].config(text = id_text)

class BasicTeamPanelWidget(LabelFrame):
	def __init__(self, master, team_title, team_type, \
		fn_update_team_name, player_info_widget_T = BasicPlayerInfoWidget, \
		**options):
		super().__init__(master, text = team_title, name = team_title, \
			**options)
		self.pack()

		self._team_type = team_type
		self._fn_update_team_name = fn_update_team_name
		self._player_info_widget_T = player_info_widget_T

		self._player_widgets = {}
		self._entry_team_name = None

		self._setup_layout()

	def _setup_layout(self):
		setting_panel = Frame(self)
		setting_panel.pack(fill = X)
		label_name = Label(setting_panel, text = "Name: ")
		label_name.pack(side = LEFT)
		self._entry_team_name = Entry(setting_panel, width = 8)
		self._entry_team_name.pack(side = LEFT)
		btn_setting_confirm = Button(setting_panel, text = "更新", \
			command = self._update_team_name)
		btn_setting_confirm.pack(side = LEFT)

	def _update_team_name(self):
		new_team_name = self._entry_team_name.get()
		self._fn_update_team_name(self._team_type, new_team_name)

	def add_player(self, player_info, color_list):
		player_widget = self._player_info_widget_T(self, player_info, color_list)
		player_widget.pack()
		player_widget.refresh()
		self._player_widgets[player_info.IP] = player_widget

	def delete_player(self, player_info):
		player_widget = self._player_widgets[player_info.IP]
		player_widget.pack_forget()
		player_widget.destroy()