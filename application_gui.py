"""@package docstring
The user interface of the application.
Provide the information or set up application variables
in the gui.
"""

import tkinter as tk

from widget_color_manager import ColorManagerWidget

class ApplicationGUI:
	"""The user interface of the application.

	@var _color_position_finder The color position finder
	@var _main_window The object of the top level window
	"""

	def __init__(self, camera, color_position_finder):
		"""Constructor

		@param color_position_finder The color position finder
		"""
		self._camera = camera
		self._color_position_finder = color_position_finder
		self._main_window = tk.Tk()
		self._setup_gui()

	def _setup_gui(self):
		"""Set up the layout of the gui
		"""
		self._color_manager = ColorManagerWidget(self._main_window, \
			self._camera, self._color_position_finder)
		self._color_manager.pack()

	def start_gui(self):
		"""Start the gui
		"""
		self._main_window.mainloop()
		return self
