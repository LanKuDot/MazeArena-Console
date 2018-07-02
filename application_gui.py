"""@package docstring
The user interface of the application.
Provide the information or set up application variables
in the gui.
"""

from tkinter import *

class ApplicationGUI:
	"""The user interface of the application.

	@var _color_position_finder The color position finder
	@var _main_window The object of the top level window
	"""

	def __init__(self, color_position_finder):
		"""Constructor

		@param color_position_finder The color position finder
		"""
		self._color_position_finder = color_position_finder
		self._main_window = Tk()
		self._setup_gui()

	def _setup_gui(self):
		"""Set up the layout of the gui
		"""
		# Set up the option panel
		option_panel = Frame(self._main_window)
		option_panel.pack()
		btn_select_color = Button(option_panel, text = "Select Color", command = self._color_position_finder.select_colors)
		btn_select_color.pack(side = LEFT)

	def start_gui(self):
		"""Start the gui
		"""
		self._main_window.mainloop()
		return self
