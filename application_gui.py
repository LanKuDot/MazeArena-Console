"""@package docstring
The user interface of the application.
Display the information or set up application variables
in the gui.
"""

import tkinter as tk

from webcam import WebCamera
from widget_color_manager import ColorManagerWidget

# Workers
_camera = WebCamera(src = 0, width = 1080, height = 720)

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
	"""

	# Set up layouts
	color_manager = ColorManagerWidget(main_window, \
		_camera, name = "color_manager")
	color_manager.pack()