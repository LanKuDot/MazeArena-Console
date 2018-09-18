"""@package docstring
The user interface of the application.
Display the information or set up application variables
in the gui.
"""

import tkinter as tk

from webcam import WebCamera
from color_position_finder import *
from maze_manager import MazeManager
from widget_color_manager import ColorManagerWidget
from widget_server_manager import WidgetServerManager

### Workers ###
_camera = WebCamera(src = 0, width = 1080, height = 720)
# Each for maze, car_team_a, car_team_b
_color_pos_finders = ColorPosFinderHolder( \
	ColorPositionFinder(_camera), \
	ColorPositionFinder(_camera), \
	ColorPositionFinder(_camera))
_maze_manager = MazeManager(_color_pos_finders)

def start_gui():
	"""Start the gui
	"""
	main_window = tk.Tk()
	_setup_gui(main_window)

	_camera.start_camera_thread()

	main_window.mainloop()

	_camera.stop_camera_thread()

def _setup_gui(main_window):
	"""Set up the layout of the gui

	@param main_window The main window of the application
	"""
	color_manager = ColorManagerWidget(main_window, \
		_camera, _color_pos_finders, _maze_manager, \
		name = "color_manager")
	color_manager.pack(side = tk.LEFT)
	server_manager = WidgetServerManager(main_window, \
		name = "server_manager")
	server_manager.pack(side = tk.RIGHT, expand = tk.Y, \
		anchor = tk.N)