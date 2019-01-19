"""@package docstring
The user interface of the application.
Display the information or set up application variables
in the gui.
"""

import tkinter as tk
import logging

from webcam import WebCamera
from color_position_finder import *
from maze_manager import MazeManager
from widget_color_manager import ColorManagerWidget
from widget_server_manager import WidgetServerManager
from config_manager import ConfigManager

from game_maze_run import GameCore, GameConsoleWidget

### Workers ###
_config_manager = ConfigManager("config.xml")
_camera = WebCamera(src = 0, width = 1080, height = 720)
_color_pos_manager = ColorPosManager(_camera, fps = 30)
_maze_manager = MazeManager(_color_pos_manager, fps = 30)
_game_core = GameCore(_maze_manager)

def start_gui():
	"""Start the gui
	"""
	main_window = tk.Tk()
	main_window.title("MazeArena console")
	_setup_gui(main_window)

	logger = logging.getLogger(__name__)
	logger.debug("Application GUI created.")

	_camera.start_camera_thread()

	try:
		main_window.mainloop()
	except KeyboardInterrupt:
		logger.error("User keyboard interrupt. Forcely shutdown.")

	_camera.stop_camera_thread()
	_camera.release_camera()

	logger.debug("Application GUI destoried.")

def _setup_gui(main_window):
	"""Set up the layout of the gui

	@param main_window The main window of the application
	"""
	color_manager = ColorManagerWidget(main_window, \
		_camera, _config_manager, _color_pos_manager, _maze_manager, \
		name = "color_manager")
	color_manager.pack(side = tk.LEFT, anchor = tk.N)
	right_frame = tk.Frame(main_window)
	right_frame.pack(side = tk.RIGHT, fill = tk.Y)
	server_manager = WidgetServerManager(right_frame, _config_manager, \
		name = "server_manager")
	server_manager.pack(anchor = tk.W)
	game_console = GameConsoleWidget(right_frame, \
		_game_core, _maze_manager)
	game_console.pack(fill = tk.BOTH, expand = tk.Y)