"""@package docstring
The widget for displaying the status of the maze.
And manage the colors to be found in the maze.
"""

from color_position_finder import ColorPositionFinder
from webcam import WebCamera

from tkinter import *
import cv2

class ColorLabel(Button):
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
	@var _color_label_panel The Frame widget that stores the
	     ColorLabel buttons
	@var _button_toggle_recognition The button widget that can
	     toggle the color recognition thread
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
		button_show_detect_img = Button(option_panel, \
			text = "Show detect image", command = self._show_result)
		button_show_detect_img.pack(fill = X)

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
		"""
		# Start color recognition
		if not self._color_position_finder.is_recognition_thread_started():
			self._color_position_finder.start_recognition_thread()
			self._button_toggle_recognition.config(text = "Stop recogniton")
		# Stop color recognition
		else:
			self._color_position_finder.stop_recognition_thread()
			self._button_toggle_recognition.config(text = "Start recognition")

	def _show_result(self):
		pass
