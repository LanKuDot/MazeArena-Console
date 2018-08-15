"""@package docstring
The widget for displaying the status of the maze.
And manage the colors to be found in the maze.
"""

from color_position_finder import ColorPositionFinder
from color_position_finder import ColorPositionFinderHolder
from webcam import WebCamera

from enum import Enum
from threading import Thread
from tkinter import *
import cv2

class ColorLabel(Button):
	"""A button widget that manage a color

	User can configure the color by clicking the button, which will pop up
	a setting window. In the setting window, user can set the color type
	or delete that color.

	@var _color The color managed by this widget in BGR domain
	@var _color_type The color type. See ColorLabel.Type
	@var _selected_color_type The color type selected in the setting window
	@var _fn_update_color The function hook that will do futher updates when
	     the color information is updated. It will be
	     ColorManagerWidget._update_color_finder().
	@var _setting_panel The setting panel widget
	"""

	class Type(Enum):
		"""The representation of colors in the maze arena

		@var NOT_DEFINED enum = 0 The color that haven't be defined yet
		@var MAZE_UPPER_PLANE enum = 1 The color that marks the upper plane of the maze
		@var MAZE_LOWER_PLANE enum = 2 The color that marks the lower plane of the maze
		@var MAZEC_CAR_TEAM_A enum = 3 The color that marks the maze cars of one team
		@var MAZEC_CAR_TEAM_B enum = 4 The color that marks the maze cars of another team
		"""
		NOT_DEFINED = 0
		MAZE_UPPER_PLANE = 1
		MAZE_LOWER_PLANE = 2
		MAZE_CAR_TEAM_A = 3
		MAZE_CAR_TEAM_B = 4

	def __init__(self, master = None, color_bgr = [0, 0, 0], fn_update_color = None, \
		**options):
		"""Constructor

		The text of the button will be set to "[B, G, R]" and the background
		color will be set to the color_bgr. The callback function of the
		button is ColorLabel._show_setting_panel().

		@param master Specify the parent widget
		@param color_bgr Specify the color in BGR domain
		@param fn_update_color The function that needs the updated information of
		       color
		@param options Other options for the Button widget
		"""
		super().__init__(master, text = color_bgr.__str__(), \
			bg = "#%02x%02x%02x" % (color_bgr[2], color_bgr[1], color_bgr[0]), \
			command = self._show_setting_panel, **options) # bg is in RGB domain
		self.pack()

		self._color = color_bgr
		self._color_type = ColorLabel.Type.NOT_DEFINED.name
		self._selected_color_type = StringVar(self, ColorLabel.Type.NOT_DEFINED.name)
		self._fn_update_color = fn_update_color

		self._setting_panel = None

	def _show_setting_panel(self):
		"""Pop up a setting window for user to configure the color.

		If the window has been already opened, foucs to that window.

		It looks like:
		+-----------------------------+
		| Color Type: [Not Defined -] |
		|  [Delete][Confirm][Cancel]  |
		+-----------------------------+
		"""
		if not self._setting_panel == None:
			self._setting_panel.focus()
			return

		self._setting_panel = Toplevel()
		self._setting_panel.title("Color config")
		self._setting_panel.geometry("%dx%d%+d%+d" % (250, 100, 100, 50))
		# Run _close_setting_panel when the user click X on the window
		self._setting_panel.protocol("WM_DELETE_WINDOW", self._close_setting_panel)

		main_panel = Frame(self._setting_panel)
		main_panel.pack(side = TOP, fill = X)
		title = Label(main_panel, text = "Color Type", anchor = W)
		title.pack(side = LEFT)
		self._selected_color_type.set(self._color_type)	# Set display text to the type of color
		color_type_list = [name for name, member in ColorLabel.Type.__members__.items()]
		om_set_color_type = OptionMenu(main_panel, self._selected_color_type, *color_type_list)
		om_set_color_type.pack(side = LEFT, expand = TRUE, anchor = W)

		bottom_panel = Frame(self._setting_panel)
		bottom_panel.pack(side = BOTTOM, padx = 2)
		btn_delete = Button(bottom_panel, text = "Delete", foreground = "red")
		btn_delete.pack(side = LEFT)
		btn_confirm = Button(bottom_panel, text = "Confirm", \
			command = self._setup_confirm)
		btn_confirm.pack(side = LEFT)
		btn_cancel = Button(bottom_panel, text = "Cancel", \
			command = self._close_setting_panel)	# Do nothing when canceled
		btn_cancel.pack(side = LEFT)

		# TopLevel automatically runs without mainloop() call

	def _close_setting_panel(self):
		"""Destory the setting window and set ColorLabel._setting_panel to None
		"""
		self._setting_panel.destroy()
		self._setting_panel = None

	def _setup_confirm(self):
		"""Reflect the modification and close the setting window

		The callback function of the confirm option in the setting window.
		The color type selected in the setting will be updated to ColorLabel._color_type
		"""
		_old_color_type = self._color_type
		self._color_type = self._selected_color_type.get()
		self._fn_update_color(self._color, _old_color_type, self._color_type)
		self._close_setting_panel()

class ColorManagerWidget(LabelFrame):
	"""A widget that manage the colors to be found in the video stream

	The user can specify the colors and manage the colors in the widget

	@var _camera The camera object for getting frames
	@var _frame The frame got from _camera
	@var _show_result_image_thread A thread that displaying the
	     recognition result
	@var _is_show_result_thread_started Is the _show_result_image_thread
	     started?
	@var _option_panel The Frame widget that contains option buttons
	@var _color_label_panel The Frame widget that contains the
	     ColorLabel buttons
	"""

	def __init__(self, master, camera: WebCamera, **options):
		"""Constructor

		@param master The parent widget of the ColorManagerWidget
		@param camera The WebCamera object
		@param options Additional options for the LabelFrame
		"""
		super().__init__(master, text = "Color Manager", **options)
		self.pack()

		self._camera = camera
		self._frame = None
		# Each for maze, car team A, and car team B
		self._color_pos_finders = ColorPositionFinderHolder( \
			ColorPositionFinder(camera), \
			ColorPositionFinder(camera), \
			ColorPositionFinder(camera))

		self._show_result_image_thread = None
		self._is_show_result_thread_started = False

		self._option_panel = None
		self._color_label_panel = None
		self._setup_layout()

	def _setup_layout(self):
		"""Set up the layout of ColorManagerWidget

		Layout as below:
		+---------------------+--------------+
		| options             | color labels |
		+---------------------+--------------+
		| select color        | colors to    |
		| Toggle recognition  | be found     |
		| show result         |              |
		+---------------------+--------------+
		"""
		self._option_panel = Frame(self)
		self._option_panel.pack(side = LEFT, fill = Y)
		label_option = Label(self._option_panel, \
			text = "Option", anchor = W)
		label_option.pack(fill = X)
		button_select_color = Button(self._option_panel, \
			text = "Select color", command = self._start_select_color_thread, \
			name = "btn_select_color")
		button_select_color.pack(fill = X)
		button_toggle_recognition = Button(self._option_panel, \
			text = "Start recognition", command = self._toggle_color_recognition, \
			name = "btn_toggle_recognition")
		button_toggle_recognition.pack(fill = X)
		button_show_result_img = Button(self._option_panel, \
			text = "Show detect image", command = self._toggle_show_result_image, \
			state = DISABLED, \
			name = "btn_show_result_img")
		button_show_result_img.pack(fill = X)

		self._color_label_panel = Frame(self)
		self._color_label_panel.pack(side = RIGHT, fill = Y)
		label_color = Label(self._color_label_panel, \
			text = "Colors", anchor = W)
		label_color.pack(fill = X)

	def _start_select_color_thread(self):
		"""Start a new thread to select the color to be found

		The callback function of the color selection option. The method will:
		* disable color selection option to prevent user from
		  clicking it more than twice;
		* disable recognition toggling option to avoid starting recognition
		  before the color selection.
		The new thread will run ColorManagerWidget._select_color().
		"""
		self._option_panel.children["btn_select_color"].config(state = DISABLED)
		self._option_panel.children["btn_toggle_recognition"].config(state = DISABLED)
		select_color_thread = Thread(target = self._select_color)
		select_color_thread.start()

	def _select_color(self):
		"""Select colors to be find in the frame

		The method will pop up a window showing the stream from the camera
		for the user to select colors.

		Use left mouse click to specify the color and press 'q' to confirm
		the selection, close the window, and automatically stop the thread
		create by self._start_select_color_thread().
		And then the color selection option and recognition toggling option
		will be enabled again.
		"""
		windowName = "Select target color (q to quit)"
		cv2.namedWindow(windowName)
		cv2.setMouseCallback(windowName, self._click_new_color)

		print("[Widget ColorManager] Color selection thread is started.")

		while True:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

			self._frame = self._camera.get_frame()
			cv2.imshow(windowName, self._frame)

		print("[Widget ColorManager] Color selection thread is started.")

		cv2.destroyWindow(windowName)
		self._option_panel.children["btn_select_color"].config(state = NORMAL)
		self._option_panel.children["btn_toggle_recognition"].config(state = NORMAL)

	def _click_new_color(self, event, x, y, flags, param):
		"""The callback function of select new color in self._select_color()

		When the left mouse click releases, store the color at where
		the mouse point is in the frame. And then create a new ColorLabel for
		user to do futher configuration.
		"""
		if event == cv2.EVENT_LBUTTONUP:
			target_color = [self._frame[y, x][0], self._frame[y, x][1], self._frame[y, x][2]]
			new_color_label = ColorLabel(self._color_label_panel, target_color, self._update_color_finder)
			new_color_label.pack(fill = X)

	def _update_color_finder(self, color_bgr, old_type, new_type):
		def _get_color_finder_by_type(color_type):
			"""Get the corresponding ColorPositionFinder by the type of the color

			The mapping of the color type to the ColorPositionFinder in the
			ColorPositionFinderHolder:
			* NOT_DEFINED -> None
			* MAZE_LOWER_PLANE -> ColorPositionFinderHolder.maze
			* MAZE_UPPER_PLANE -> ColorPositionFinderHolder.maze
			* MAZE_CAR_TEAM_A -> ColorPositionFinderHolder.car_team_a
			* MAZE_CAR_TEAM_B -> ColorPositionFinderHolder.car_team_b

			@param color_type The type of the color
			@return The corresponding ColorPositionFinder. None if the color type
			        is NOT_DEFINED or not existing.
			"""
			return {
				ColorLabel.Type.MAZE_LOWER_PLANE.name: self._color_pos_finders.maze,
				ColorLabel.Type.MAZE_UPPER_PLANE.name: self._color_pos_finders.maze,
				ColorLabel.Type.MAZE_CAR_TEAM_A.name:  self._color_pos_finders.car_team_a,
				ColorLabel.Type.MAZE_CAR_TEAM_B.name:  self._color_pos_finders.car_team_b
			}.get(color_type)

		old_color_finder = _get_color_finder_by_type(old_type)
		new_color_finder = _get_color_finder_by_type(new_type)

		if old_color_finder == new_color_finder:
			return
		if not old_color_finder == None:
			old_color_finder.delete_target_color(*color_bgr)
		if not new_color_finder == None:
			new_color_finder.add_target_color(*color_bgr)

	def _toggle_color_recognition(self):
		"""Toggle the color recognition thread in ColorPositionFinder

		If the recognition thread is started:
		* enable show recognition result option;
		* disable selecting color option.
		If the thread is stopped:
		* toggle two options mentioned above;
		* stop the show result thread if it's running.
		"""
		# Start color recognition
		if not self._color_position_finder.is_recognition_thread_started():
			self._color_position_finder.start_recognition_thread()
			# TODO Currently you cannot select new color while recognizing
			self._option_panel.children["btn_select_color"].config(state = DISABLED)
			self._option_panel.children["btn_toggle_recognition"].config(text = "Stop recogniton")
			self._option_panel.children["btn_show_result_img"].config(state = NORMAL)
		# Stop color recognition
		else:
			if self._is_show_result_thread_started:
				self._toggle_show_result_image()
			self._color_position_finder.stop_recognition_thread()
			self._option_panel.children["btn_select_color"].config(state = NORMAL)
			self._option_panel.children["btn_toggle_recognition"].config(text = "Start recognition")
			self._option_panel.children["btn_show_result_img"].config(state = DISABLED)

	def _toggle_show_result_image(self):
		"""Toggle the thread of showing recognition result image
		"""
		# Start showing recognition result
		if not self._is_show_result_thread_started:
			self._option_panel.children["btn_show_result_img"].config(text = "Hide detect image")
			self._show_result_image_thread = \
				Thread(target = self._show_result_image)
			self._show_result_image_thread.start()
			self._is_show_result_thread_started = True
		# Stop showing recognition result
		else:
			self._option_panel.children["btn_show_result_img"].config(text = "Show detect image")
			self._is_show_result_thread_started = False
			self._show_result_image_thread.join()

	def _show_result_image(self):
		"""Display the color recognition result in a window.

		The method will invoke ColorManagerWidget._mark_recognition_result()
		to mark the colors found and then show the marked frame to the user.
		"""
		window_name = "Recognition result (q to quit)"
		cv2.namedWindow(window_name)

		print("[Widget ColorManager] Show result image thread is started.")

		while self._is_show_result_thread_started:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				self._option_panel.children["btn_show_result_img"]. \
					config(text = "Show detect image")
				self._is_show_result_thread_started = False
				break

			self._frame = self._camera.get_frame()
			self._mark_recognition_result()
			cv2.imshow(window_name, self._frame)

		print("[Widget ColorManager] Show result image thread is stopped.")

		cv2.destroyWindow(window_name)

	def _mark_recognition_result(self):
		"""Mark the recogntion result to the original frame

		The method will get a target color list from ColorPositionFinder
		by invoking ColorPositionFinder.get_all_target_colors().
		Then, take recognition result stored in the
		ColorPosition.pixel_position of each color in the target color list
		and mark red dots at these positions.
		"""
		colors = self._color_position_finder.get_all_target_colors()
		for color_id in range(len(colors)):
			posFound = colors[color_id].pixel_position
			for i in range(len(posFound)):
				cv2.circle(self._frame, (posFound[i].x, posFound[i].y), \
					5, (0, 0, 150), -1)
