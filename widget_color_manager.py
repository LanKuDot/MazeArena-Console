"""@package docstring
The widget for displaying the status of the maze.
And manage the colors to be found in the maze.
"""

from color_type import ColorType
from color_position_finder import ColorPositionFinder, ColorPosFinderHolder
from util.number_entry import *
from maze_manager import MazeManager
from webcam import WebCamera

from threading import Thread
from tkinter import *
import cv2
import numpy as np

class ColorLabel(Button):
	"""A button widget that manage a color

	User can configure the color by clicking the button, which will pop up
	a setting window. In the setting window, user can set the color type
	or delete that color.

	@var _color The color managed by this widget in BGR domain
	@var _color_type The color type. See ColorType
	@var _selected_color_type The color type selected in the setting window
	@var _fn_update_color The function hook that will do futher updates when
	     the color information is updated. It will be
	     ColorManagerWidget._update_color_finder().
	@var _entry_LED_height The Entry widget for entering the height of the LED
	     on the car
	@var _setting_panel The setting panel widget
	"""

	def __init__(self, master = None, color_bgr = [0, 0, 0], fn_update_color = None, \
		**options):
		"""Constructor

		The text of the button will be set to default ColorType (ColorType.NOT_DEFINED)
		and the background color will be set to the color_bgr.
		The callback function of the button is ColorLabel._show_setting_panel().

		@param master Specify the parent widget
		@param color_bgr Specify the color in BGR domain
		@param fn_update_color The function that needs the updated information of
		       color
		@param options Other options for the Button widget
		"""
		super().__init__(master, text = ColorType.NOT_DEFINED.__str__(), \
			bg = "#%02x%02x%02x" % (color_bgr[2], color_bgr[1], color_bgr[0]), \
			command = self._show_setting_panel, **options) # bg is in RGB domain
		self.pack()

		self._color = color_bgr
		self._color_hsv = cv2.cvtColor(np.uint8([[color_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
		self._color_type = ColorType.NOT_DEFINED
		self._selected_color_type = StringVar(self, ColorType.NOT_DEFINED.name)
		self._selected_color_type.trace("w", self._toggle_entry_LED_height)
		self._fn_update_color = fn_update_color
		self._LED_height = 0.0
		self._entry_LED_height = None

		self._setting_panel = None

	def _show_setting_panel(self):
		"""Pop up a setting window for user to configure the color.

		If the window has been already opened, foucs to that window.

		It looks like:
		+-----------------------------+
		| BGR: #BGR                   |
		| HSV: #HSV                   |
		| Color Type: [Not Defined -] |
		| Car height: [ ] cm          |
		|  [Delete][Confirm][Cancel]  |
		+-----------------------------+
		"""
		if not self._setting_panel == None:
			self._setting_panel.focus()
			return

		self._setting_panel = Toplevel()
		self._setting_panel.title("顏色設定")
		self._setting_panel.geometry("%dx%d%+d%+d" % (250, 120, 100, 50))
		# Run _close_setting_panel when the user click X on the window
		self._setting_panel.protocol("WM_DELETE_WINDOW", self._close_setting_panel)

		# Display color information
		label_bgr = Label(self._setting_panel, \
			text = "BGR: ({:03d}, {:03d}, {:03d})" \
			.format(self._color[0], self._color[1], self._color[2]), \
			anchor = W)
		label_bgr.pack(side = TOP, fill = X)
		label_hsv = Label(self._setting_panel, \
			text = "HSV: ({:03d}, {:03d}, {:03d})" \
			.format(self._color_hsv[0], self._color_hsv[1], self._color_hsv[2]), \
			anchor = W)
		label_hsv.pack(side = TOP, fill = X)

		color_type_panel = Frame(self._setting_panel)
		color_type_panel.pack(side = TOP, fill = X)
		ct_title = Label(color_type_panel, text = "顏色類別", anchor = W)
		ct_title.pack(side = LEFT)
		# Set display text to the type of color
		self._selected_color_type.set(self._color_type.name)
		color_type_list = [name for name, member in ColorType.__members__.items()]
		om_set_color_type = OptionMenu(color_type_panel, self._selected_color_type, \
			*color_type_list)
		om_set_color_type.pack(side = LEFT, expand = TRUE, anchor = W)

		LED_height_panel = Frame(self._setting_panel)
		LED_height_panel.pack(fill = X)
		lhp_label_1 = Label(LED_height_panel, text = "車輛高度: ")
		lhp_label_1.pack(side = LEFT)
		self._entry_LED_height = NonNegativeFloatEntry(LED_height_panel, width = 4)
		self._entry_LED_height.insert(0, str(self._LED_height)) # Set previous value
		self._entry_LED_height.pack(side = LEFT)
		lhp_label_2 = Label(LED_height_panel, text = " 公分")
		lhp_label_2.pack(side = LEFT)
		self._toggle_entry_LED_height()

		bottom_panel = Frame(self._setting_panel)
		bottom_panel.pack(side = BOTTOM, padx = 2)
		btn_delete = Button(bottom_panel, text = "刪除", foreground = "red", \
			command = self._delete_color)
		btn_delete.pack(side = LEFT)
		btn_confirm = Button(bottom_panel, text = "確認", \
			command = self._setup_confirm)
		btn_confirm.pack(side = LEFT)
		btn_cancel = Button(bottom_panel, text = "取消", \
			command = self._close_setting_panel)	# Do nothing when canceled
		btn_cancel.pack(side = LEFT)

		# TopLevel automatically runs without mainloop() call

	def _toggle_entry_LED_height(self, *args):
		"""Enable LED height entry if color type of maze car is selected

		The callback function of StringVar ColorLabel._selected_color_type if
		its value is changed. When _selected_color_type is set to
		ColorType.MAZE_CAR_TEAM_A or ColorType.MAZE_CAR_TEAM_B,
		ColorLabel._entry_LED_height is enabled for entering value.
		Otherwise, it will be disabled.
		"""
		try:
			self._entry_LED_height.focus()
		except Exception:
			return

		cur_color_type = ColorType[self._selected_color_type.get()]
		toggle = {
			ColorType.MAZE_CAR_TEAM_A: NORMAL,
			ColorType.MAZE_CAR_TEAM_B: NORMAL
		}.get(cur_color_type, DISABLED)
		self._entry_LED_height.config(state = toggle)

	def _close_setting_panel(self):
		"""Destory the setting window and set ColorLabel._setting_panel to None
		"""
		self._setting_panel.destroy()
		self._setting_panel = None

	def _setup_confirm(self):
		"""Confirm and reflect the modification to the color manager and Mazemanager

		The callback function of the confirm option in the setting window.
		The color type selected in the setting is updated to ColorLabel._color_type
		and set the button text to the selected color type.
		The valid LED height value is updated to ColorLabel._LED_height.
		Then invoke ColorLabel._fn_update_color() to update changes.
		"""
		_old_color_type = self._color_type
		self._color_type = ColorType[self._selected_color_type.get()]
		self.config(text = self._color_type.__str__())
		self._LED_height = float(self._entry_LED_height.get())
		self._fn_update_color(self._color, _old_color_type, self._color_type, self._LED_height)
		self._close_setting_panel()

	def _delete_color(self):
		"""Delete the color and reflect the modification to the color manager

		The callback function of the delete option in the setting window.
		Invoke ColorLabel._fn_update_color() to update changes, and
		the ColorLabel this color belongs will be deleted.
		"""
		if not self._color_type == ColorType.NOT_DEFINED:
			self._fn_update_color(self._color, self._color_type, None)
		self._close_setting_panel()
		self.pack_forget()
		self.destroy()

class ColorManagerWidget(LabelFrame):
	"""A widget that manage the colors to be found in the video stream

	The user can specify the colors and manage the colors in the widget

	@var _camera The camera object for getting frames
	@var _frame The frame got from _camera
	@var _color_pos_finders The instance of class ColorPosFinderHolder
	@var _maze_manager The instance of class MazeManager
	@var _show_result_image_thread A thread that displaying the
	     recognition result
	@var _is_show_result_thread_started Is the _show_result_image_thread
	     started?
	@var _option_panel The Frame widget that contains option buttons
	@var _color_label_panel The Frame widget that contains the
	     ColorLabel buttons
	@var _maze_info_entries The dict that stores the Entry widgets for
	     gathering the information of the maze
	"""

	def __init__(self, master, camera: WebCamera, \
		color_pos_finders: ColorPosFinderHolder, \
		maze_manager: MazeManager, **options):
		"""Constructor

		@param master The parent widget of the ColorManagerWidget
		@param camera The WebCamera object
		@param color_pos_finders The instance of class ColorPosFinderHolder
		@param maze_manager The instance of class MazeManager
		@param options Additional options for the LabelFrame
		"""
		super().__init__(master, text = "顏色管理", **options)
		self.pack()

		self._camera = camera
		self._frame = None
		self._color_pos_finders = color_pos_finders
		self._maze_manager = maze_manager

		self._show_result_image_thread = None
		self._is_show_result_thread_started = False

		self._option_panel = None
		self._color_label_panel = None
		self._maze_info_entries = {
			'x_scale': None, \
			'y_scale': None, \
			'wall_height': None}
		self._setup_layout()

	def _setup_layout(self):
		"""Set up the layout of ColorManagerWidget

		Layout as below:
		+---------------------+--------------+
		| options             | color labels |
		+---------------------+--------------+
		| select color        | colors to    |
		| recognize maze      | be found     |
		| scale: x [ ] y [ ]  |              |
		| height: [  ] cm     |              |
		| recognize maze cars |              |
		| show result         |              |
		+---------------------+--------------+
		"""
		self._option_panel = Frame(self)
		self._option_panel.pack(side = LEFT, fill = Y)
		label_option = Label(self._option_panel, \
			text = "功能", anchor = W)
		label_option.pack(fill = X)
		button_select_color = Button(self._option_panel, \
			text = "選取顏色", command = self._start_select_color_thread, \
			name = "btn_select_color")
		button_select_color.pack(fill = X)
		button_recognize_maze = Button(self._option_panel, \
			text = "辨識迷宮", command = self._maze_recognition, \
			name = "btn_recognize_maze")
		button_recognize_maze.pack(fill = X)
		#-----
		maze_scale_frame = Frame(self._option_panel)
		label_ms_1 = Label(maze_scale_frame, text = "迷宮座標：X ")
		label_ms_1.pack(side = LEFT)
		entry_maze_scale_x = PositiveIntEntry(maze_scale_frame, width = 3)
		entry_maze_scale_x.pack(side = LEFT)
		label_ms_2 = Label(maze_scale_frame, text = " Y ")
		label_ms_2.pack(side = LEFT)
		entry_maze_scale_y = PositiveIntEntry(maze_scale_frame, width = 3)
		entry_maze_scale_y.pack(side = LEFT)
		maze_scale_frame.pack()

		maze_height_frame = Frame(self._option_panel)
		label_mh_1 = Label(maze_height_frame, text = "迷宮牆高：")
		label_mh_1.pack(side = LEFT)
		entry_maze_height = NonNegativeFloatEntry(maze_height_frame, width = 5)
		entry_maze_height.pack(side = LEFT)
		label_mh_2 = Label(maze_height_frame, text = " 公分")
		label_mh_2.pack(side = LEFT)
		maze_height_frame.pack(fill = X)

		self._maze_info_entries['x_scale'] = entry_maze_scale_x
		self._maze_info_entries['y_scale'] = entry_maze_scale_y
		self._maze_info_entries['wall_height'] = entry_maze_height
		#-----
		button_recognize_maze_car = Button(self._option_panel, \
			text = "辨識車輛位置", command = self._toggle_car_recognition, \
			name = "btn_recognize_maze_cars")
		button_recognize_maze_car.pack(fill = X)
		button_show_result_img = Button(self._option_panel, \
			text = "顯示標記影像", command = self._toggle_show_result_image, \
			state = DISABLED, \
			name = "btn_show_result_img")
		button_show_result_img.pack(fill = X)

		self._color_label_panel = Frame(self)
		self._color_label_panel.pack(side = RIGHT, fill = Y)
		label_color = Label(self._color_label_panel, \
			text = "目標辨識顏色", anchor = W)
		label_color.pack(fill = X)

	def _start_select_color_thread(self):
		"""Start a new thread to select the color to be found

		The callback function of the color selection option. The method will:
		* disable color selection option to prevent user from
		  clicking it more than twice;
		* disable recognition toggling options to avoid starting recognition
		  before the color selection.
		The new thread will run ColorManagerWidget._select_color(), and
		the thread will be automatically stopped after finishing color selection.
		"""
		self._option_panel.children["btn_select_color"].config(state = DISABLED)
		self._option_panel.children["btn_recognize_maze"].config(state = DISABLED)
		self._option_panel.children["btn_recognize_maze_cars"].config(state = DISABLED)
		select_color_thread = Thread(target = self._select_color)
		select_color_thread.start()

	def _select_color(self):
		"""Select colors to be find in the frame

		The method will pop up a window showing the stream from the camera
		for the user to select colors.

		Use left mouse click to specify the color and press 'q' to confirm
		the selection, close the window, and automatically stop the thread
		create by self._start_select_color_thread().
		And then the color selection option and recognition toggling options
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

		print("[Widget ColorManager] Color selection thread is stopped.")

		cv2.destroyWindow(windowName)
		self._option_panel.children["btn_select_color"].config(state = NORMAL)
		self._option_panel.children["btn_recognize_maze"].config(state = NORMAL)
		self._option_panel.children["btn_recognize_maze_cars"].config(state = NORMAL)

	def _click_new_color(self, event, x, y, flags, param):
		"""The callback function of select new color in self._select_color()

		When the left mouse click releases, store the color at where
		the mouse point is in the frame. And then create a new ColorLabel for
		user to do futher configuration.
		"""
		if event == cv2.EVENT_LBUTTONUP:
			target_color = [self._frame[y, x][0], self._frame[y, x][1], self._frame[y, x][2]]
			new_color_label = ColorLabel(self._color_label_panel, target_color, self._update_color)
			new_color_label.pack(fill = X)

	def _update_color(self, color_bgr, \
		old_type: ColorType, new_type: ColorType, LED_height = 0.0):
		"""Assign, change, or delete the color in ColorPositionFinders and MazeManager

		The action will be taken accroding to old_type and new_type.
		For example:
		* `(color_A, None, ColorType.MAZE_LOWER_PLANE)`:
		  color_A is assigned to the ColorPositionFinder of maze
		* `(color_A, ColorType.MAZE_LOWER_PLANE, ColorType.MAZE_CAR_TEAM_A)`:
		  color_A is moved from the ColorPositionFinder of maze to that of car_team_a
		* `(color_A, ColorType.MAZE_CAR_TEAM_A, None)`:
		  color_A is deleted from the ColorPositionFinder of car_team_a

		@param color_bgr Specify the target color in BGR domain
		@param old_type Specify the previous type of the color_bgr
		@param new_type Specify the new type of the color_bgr
		@param LED_height Specify the height of the LED on the maze car
		       (if the new_type is MAZE_CAR_TEAM_A or MAZE_CAR_TEAM_B, this value is needed.)
		"""
		# Update MazeManager
		self._maze_manager.set_color(color_bgr, old_type, new_type, LED_height)

		# Update ColorPositionFinder
		old_color_finder = self._color_pos_finders.get_posFinder_by_type(old_type)
		new_color_finder = self._color_pos_finders.get_posFinder_by_type(new_type)

		if old_color_finder == new_color_finder:
			return
		if not old_color_finder == None:
			old_color_finder.delete_target_color(*color_bgr)
		if not new_color_finder == None:
			new_color_finder.add_target_color(*color_bgr)

	def _maze_recognition(self):
		"""Recognize the maze

		The recognition will be automatically stopped when the maze manger
		finished generating maze position transform matrix.
		"""
		# Check if the input value is vaild
		x_scale = self._maze_info_entries['x_scale'].get()
		y_scale = self._maze_info_entries['y_scale'].get()
		wall_height = self._maze_info_entries['wall_height'].get()
		if not x_scale or not y_scale or not wall_height:
			print('[Widget ColorManager] There are some invalid input value. ' \
				'x: %s, y: %s, wall_height: %s' % (x_scale, y_scale, wall_height,))
			return

		self._color_pos_finders.maze.start_recognition_thread()
		self._option_panel.children["btn_recognize_maze"].config(text = "辨識中...")

		self._maze_manager.set_maze(int(x_scale), int(y_scale), float(wall_height))
		self._maze_manager.recognize_maze()

		self._color_pos_finders.maze.stop_recognition_thread()
		self._option_panel.children["btn_recognize_maze"].config(text = "辨識迷宮")

	def _toggle_car_recognition(self):
		"""Toggle the color recognition of maze cars

		ColorPositionFinders of car_team_a and car_team_b will be toggled.
		"""
		# Start color recognition
		if not self._color_pos_finders.car_team_a.is_recognition_thread_started():
			self._color_pos_finders.car_team_a.start_recognition_thread()
			self._color_pos_finders.car_team_b.start_recognition_thread()
			self._option_panel.children["btn_recognize_maze_cars"].config(text = "停止辨識位置")
			self._option_panel.children["btn_show_result_img"].config(state = NORMAL)
		# Stop color recognition
		else:
			self._color_pos_finders.car_team_a.stop_recognition_thread()
			self._color_pos_finders.car_team_b.stop_recognition_thread()
			self._option_panel.children["btn_recognize_maze_cars"].config(text = "辨識車輛位置")
			self._option_panel.children["btn_show_result_img"].config(state = DISABLED)

	def _toggle_show_result_image(self):
		"""Toggle the thread of showing recognition result image
		"""
		# Start showing recognition result
		if not self._is_show_result_thread_started:
			self._option_panel.children["btn_show_result_img"].config(text = "關閉標記影像")
			self._show_result_image_thread = \
				Thread(target = self._show_result_image)
			self._show_result_image_thread.start()
			self._is_show_result_thread_started = True
		# Stop showing recognition result
		else:
			self._option_panel.children["btn_show_result_img"].config(text = "顯示標記影像")
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
					config(text = "顯示標記影像")
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
		def _mark_dots(color_pos_finder, marking_color):
			colors = color_pos_finder.get_all_target_colors()
			for color_id in range(len(colors)):
				posFound = colors[color_id].pixel_position
				for i in range(len(posFound)):
					cv2.circle(self._frame, (posFound[i].x, posFound[i].y), \
						5, marking_color, -1)

		_mark_dots(self._color_pos_finders.maze, (0, 0, 150))
		_mark_dots(self._color_pos_finders.car_team_a, (0, 150, 0))
		_mark_dots(self._color_pos_finders.car_team_b, (150, 0, 0))
