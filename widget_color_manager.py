"""@package docstring
The widget for displaying the status of the maze.
And manage the colors to be found in the maze.
"""

from color_position_finder import ColorPositionFinder
from webcam import WebCamera

from enum import Enum
from threading import Thread
from tkinter import *
import cv2

class ColorLabel(Button):
	class Type(Enum):
		"""The representation of colors in the maze arena

		@var MAZE_UPPER_PLANE enum = 1 The color that marks the upper plane of the maze
		@var MAZE_LOWER_PLANE enum = 2 The color that marks the lower plane of the maze
		@var MAZEC_CAR enum = 3 The color that marks the maze car
		@ver OTHER enum = 99 Undefined color
		"""
		MAZE_UPPER_PLANE = 1
		MAZE_LOWER_PLANE = 2
		MAZE_CAR = 3
		OTHER = 99

	def __init__(self, master = None, color_bgr = [0, 0, 0], **options):
		super().__init__(master, text = color_bgr.__str__(), \
			bg = "#%02x%02x%02x" % (color_bgr[2], color_bgr[1], color_bgr[0]) , \
			**options) # bg is in RGB domain
		self.pack()

		self._color = color_bgr

class ColorManagerWidget(LabelFrame):
	"""A widget that manage the colors to be found in the video stream

	The user can specify the colors and manage the colors in the widget

	@var _camera The camera object for getting frames
	@var _frame The frame got from _camera
	@var _color_pos_finder The ColorPositionFinder for updating
	     the target colors to be found in the frame
	@var _show_result_image_thread A thread that displaying the
	     recognition result
	@var _is_show_result_thread_started Is the _show_result_image_thread
	     started?
	@var _color_label_panel The Frame widget that stores the
	     ColorLabel buttons
	@var _button_toggle_recognition The button widget that can
	     toggle the color recognition thread
	@var _button_show_result_img The button widget that can
	     create a window for showing recognition result
	"""

	def __init__(self, master, camera: WebCamera, \
		color_pos_finder: ColorPositionFinder, **options):
		"""Constructor

		@param master The parent widget of the ColorManagerWidget
		@param camera The WebCamera object
		@param color_pos_finder The ColorPositionFinder object
		@param options Additional options for the LabelFrame
		"""
		super().__init__(master, text = "Color Manager", **options)
		self.pack()

		self._camera = camera
		self._frame = None
		self._color_position_finder = color_pos_finder

		self._show_result_image_thread = None
		self._is_show_result_thread_started = False

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
		option_panel = Frame(self)
		option_panel.pack(side = LEFT, fill = Y)
		label_option = Label(option_panel, \
			text = "Option", anchor = W)
		label_option.pack(fill = X)
		button_select_color = Button(option_panel, \
			text = "Select color", command = self._select_color)
		button_select_color.pack(fill = X)
		self._button_toggle_recognition = Button(option_panel, \
			text = "Start recognition", command = self._toggle_color_recognition)
		self._button_toggle_recognition.pack(fill = X)
		self._button_show_result_img = Button(option_panel, \
			text = "Show detect image", command = self._toggle_show_result_image, \
			state = DISABLED)
		self._button_show_result_img.pack(fill = X)

		self._color_label_panel = Frame(self)
		self._color_label_panel.pack(side = RIGHT, fill = Y)
		label_color = Label(self._color_label_panel, \
			text = "Colors", anchor = W)
		label_color.pack(fill = X)

	def _select_color(self):
		"""Select colors to be find in the frame

		The method will pop up a window showing the stream from the camera
		for the user to select colors.
		Use left mouse click to specify the color and press 'q' to confirm
		the selection and close the window.
		"""
		windowName = "Select target color (q to quit)"
		cv2.namedWindow(windowName)
		cv2.setMouseCallback(windowName, self._on_mouse_click)

		while True:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

			self._frame = self._camera.get_frame()
			cv2.imshow(windowName, self._frame)

		cv2.destroyWindow(windowName)

	def _on_mouse_click(self, event, x, y, flags, param):
		"""The callback function of the mouse clicking event

		When the left mouse click releases, store the color at where
		the mouse point is in the frame to ColorPositionFinder._colors_to_find.
		"""
		if event == cv2.EVENT_LBUTTONUP:
			target_color = [self._frame[y, x][0], self._frame[y, x][1], self._frame[y, x][2]]
			self._color_position_finder.add_target_color( \
				self._frame[y, x][0], self._frame[y, x][1], self._frame[y, x][2])
			new_color_label = ColorLabel(self._color_label_panel, target_color)
			new_color_label.pack(fill = X)

	def _toggle_color_recognition(self):
		"""Toggle the color recognition thread in ColorPositionFinder

		If the thread is started, enable ColorManagerWidget._button_show_result_img
		which make user can watch the recognition result.
		If the thread is stopped, then disable this button.
		"""
		# Start color recognition
		if not self._color_position_finder.is_recognition_thread_started():
			self._color_position_finder.start_recognition_thread()
			self._button_toggle_recognition.config(text = "Stop recogniton")
			self._button_show_result_img.config(state = NORMAL)
		# Stop color recognition
		else:
			self._color_position_finder.stop_recognition_thread()
			self._button_toggle_recognition.config(text = "Start recognition")
			self._button_show_result_img.config(state = DISABLED)
			if self._is_show_result_thread_started:
				self._toggle_show_result_image()

	def _toggle_show_result_image(self):
		"""Toggle the thread of showing recognition result image
		"""
		# Start showing recognition result
		if not self._is_show_result_thread_started:
			self._show_result_image_thread = \
				Thread(target = self._show_result_image)
			self._show_result_image_thread.start()
			self._is_show_result_thread_started = True
		# Stop showing recognition result
		else:
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
				break

			self._frame = self._camera.get_frame()
			self._mark_recognition_result()
			cv2.imshow(window_name, self._frame)

		print("[Widget ColorManager] Show result image thread is stopped.")

		cv2.destroyWindow(window_name)
		self._is_show_result_thread_started = False

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
