"""The widget that would be used in the game
"""

from tkinter import *
from game_essential.game_core import GameCore

class WidgetGameCommand(Frame):
	def __init__(self, master, game_core: GameCore, **options):
		super().__init__(master, **options)
		self.pack()

		self._game_core = game_core

		self._setup_layout()

	def _setup_layout(self):
		btn_toggle_game = Button(self, text = "遊戲開始", \
			command = self._toggle_game, name = "btn_toggle_game")
		btn_toggle_game.pack()

	def _toggle_game(self):
		if not self._game_core.is_game_started:
			self.game_start()
		else:
			self.game_stop()

	def game_start(self):
		self._game_core.game_start()
		self.children["btn_toggle_game"].config("遊戲停止")

	def game_stop(self):
		self._game_core.game_stop()
		self.children["btn_toggle_game"].config("遊戲開始")

class WidgetPlayerInfo(Frame):
	def __init__(self, master, player_info):
		pass

	def refresh():
		pass
