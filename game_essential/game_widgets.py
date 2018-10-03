"""The widget that would be used in the game
"""

from tkinter import *
import tkinter as tk
from game_essential.game_core import GameCore
from game_essential.player_info_table import PlayerInfo

class GameToggleButton(Button):
	"""The button that makes game start or stop

	@vat _game_core The GameCore object to be toggled
	"""

	def __init__(self, master, game_core: GameCore, **options):
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
		self.config("遊戲停止")

	def game_stop(self):
		self._game_core.game_stop()
		self.config("遊戲開始")

class PlayerInfoWidget(Frame):
	"""The widget for setting and displaying PlayerInfo

	Usage:
	```
	playerInfoWidget = PlayerInfoWidget(...)
	playerInfowidget.setup_layout() # Must invoke this method
	playerInfoWidget.pack()

	playerInfoWidget.refresh() # To reflect the changes in PlayerInfo
	```

	@var _player_info The PlayerInfo object this widget binds
	@var _fn_set_player_color The callback function for the changing
	     of the player color in the widget
	@var _selected_color_bgr The trace variable of the color selection
	     in the OptionMenu
	@var _previous_selected_color_bgr The color selected at previous time
	"""

	def __init__(self, master, player_info: PlayerInfo, \
		fn_set_player_color, **options):
		"""Constructor

		@param master The parent widget
		@param player_info The target player information to be shwon
		@param fn_set_player_color The callback function for the changing
		       of the player color in the widget.
			   It will be fn_set_player_color(player_ip, selected_color)
		@param option Other options for Frame widget
		"""
		super().__init__(master, **options)
		self.pack()

		self._player_info = player_info
		self._fn_set_player_color = fn_set_player_color
		self._selected_color_bgr = StringVar(self, "顏色未定")
		self._selected_color_bgr.trace("w", self._update_player_color)
		self._previous_selected_color_bgr = self._selected_color_bgr.get()

		self._color_menu = None

	def setup_layout(self):
		"""Set up the layout of the widget

		It will be like:
		+-------------------------+
		| [] IP ID Team [Color +] |
		+-------------------------+
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
		team = Label(self, text = "-", \
			width = 2, anchor = W, name = "team")
		team.pack(side = LEFT)
		color_list = ["顏色未定"]
		color_menu = OptionMenu(self, self._selected_color_bgr, \
			*color_list)
		color_menu.configure(width = 13)
		color_menu.pack(side = LEFT)
		self._color_menu = color_menu

	def update_color_select_menu(self, color_list):
		"""Exchange the colors selectable for this player info

		The method will destory the old options and fill
		options that specified in color_list.

		@param color_list Specify a list of colors
		"""
		self._color_menu.delete(0, 'end')
		for color in color_list:
			self._color_menu.add_command(label = color.__str__(), \
				command = tk._setit(self._selected_color_bgr, color.__str__()))

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

		self._fn_set_player_color(self._player_info.IP, color_bgr)

	def refresh(self):
		"""Make the widget refresh the displaying information
		"""
		ip_text = self._player_info.IP if self._player_info.IP else "-"
		self.children["ip"].config(text = ip_text)
		id_text = self._player_info.ID if self._player_info.ID else "-"
		self.children["id"].config(text = id_text)
		team_text = self._player_info.team if self._player_info.team else "-"
		self.children["team"].config(text = team_text)
