"""@package docstring
The manager that handling the information of the maze,
such as the size of the maze, the position of the maze cars.
"""

import cv2
import numpy as np
from operator import attrgetter
from threading import Lock

from point import Point2D
from color_type import ColorType
from color_position_finder import *
from util.job_thread import JobThread

class CarPosition:
	"""A data structure for the position of the maze car in the maze

	@var color_bgr The LED color of the maze car in BGR domain
	@var LED_height The height of the LED on the maze car
	@var position The position of the maze car in the maze
	"""

	def __init__(self, color_bgr, LED_height: float):
		"""Constructor

		@param color_bgr Specify the color of the LED on the maze car
		@param LED_height Specify the height of LED on the maze car
		"""
		self.color_bgr = color_bgr
		self.LED_height = LED_height
		self.position = Point2D(-1, -1)

	def __eq__(self, other):
		"""Predefined equal comparsion method

		Two CarPosition objects are the same if their ColorPosition.color_bgr
		is the same.

		@return True if the color is the same
		"""
		return self.color_bgr == other.color_bgr

	def __ne__(self, other):
		return not self.__eq__(other)

class MazePositionFinder:
	"""Find the position of the colors in the maze

	MazePositionFinder uses the position of the colors found in the video stream
	(which is from ColorPositionFinder) to find the position of the colors in
	the maze.

	@var _maze_color_pos_finder The ColorPosFinder that contains the reference color
	     of the maze
	@var _color_pos_finder The ColorPosFinder that contains the colors to be found
	     in the MazePositionFinder
	@var _maze_scale A Point2D(x, y) which represents the coordinate scale of
	     the maze (0 ~ x, 0 ~ y)
	@var _wall_height The height of the maze wall
	@var _upper_plane_color The color that locates the upper plane of the maze
	@var _lower_plane_color Simliar to _upper_plane_color but for the lower plane
	@var _upper_transform_mat A matrix that transform from the frame
	     coordinate to the coordinate of the upper plane of the maze
	@var _lower_transform_mat Similar to _upper_transform_mat, but for
	     the lower plane of the maze
	@var _colors_to_find A list of CarPosition
	@var _colors_to_find_lock A lock for accessing _colors_to_find
	@var _ratio_to_wall_height_array An array of the ratio of LED height to the
	     maze wall height of each color in _colors_to_find
	@var _recognition_thread A JobThread for recognizing the car position
	"""

	def __init__(self, maze_color_pos_finder: ColorPositionFinder, \
		color_pos_finder: ColorPositionFinder):
		self._maze_color_pos_finder = maze_color_pos_finder
		self._color_pos_finder = color_pos_finder

		self._maze_scale = None
		self._wall_height = None
		self._upper_plane_color = None
		self._lower_plane_color = None
		self._upper_transform_mat = None
		self._lower_transform_mat = None
		self._colors_to_find = []
		self._colors_to_find_lock = Lock()
		self._ratio_to_wall_height_array = []

		self._recognition_thread = JobThread(self._recognize_pos_in_maze, \
			"Car position recognition", 0.01)

	def set_maze(self, scale_x, scale_y, wall_height):
		"""Set the information of the maze

		@param scale_x The x scale of the maze
		@param scale_y The y scale of the maze
		@param wall_height The height of the maze wall
		"""
		self._maze_scale = Point2D(scale_x, scale_y)
		self._wall_height = wall_height

	def add_target_color(self, color_bgr, color_type: ColorType, LED_height = 0.0):
		"""Add a target color to the position finding list

		Accroding the color_type:
		- MAZE_UPPER_PLANE: The color is assigned to the
		  MazePositionFinder._upper_plane_color
		- MAZE_LOWER_PLANE: The color is assigned to the
		  MazePositionFinder._lower_plane_color
		- Others: The color is added to the MazePositionFinder._colors_to_find
		  if it is not in there. Otherwise, update the CarPosition.LED_height
		  value.

		@param color_bgr The target color in BGR domain
		@param color_type The ColorType of the target color
		@param LED_height The height of the LED on the maze car
		"""
		if self._recognition_thread.is_running:
			print("[MazePosFinder] Cannot update colors while recognizing.")
			return

		if color_type == ColorType.MAZE_UPPER_PLANE:
			self._upper_plane_color = color_bgr
			print("[MazePosFinder] Set the color of upper plane to ({0}, {1}, {2})" \
				.format(*color_bgr))
		elif color_type == ColorType.MAZE_LOWER_PLANE:
			self._lower_plane_color = color_bgr
			print("[MazePosFinder] Set the color of lower plane to ({0}, {1}, {2})" \
				.format(*color_bgr))
		else:	# Team_X
			where = -1
			try:
				where = self._colors_to_find.index(CarPosition(color_bgr, 0))
			except ValueError:
				self._colors_to_find.append(CarPosition(color_bgr, LED_height))
				print("[MazePosFinder] New color added: ({0}, {1}, {2})" \
					.format(*color_bgr))
			else:
				self._colors_to_find[where].LED_height = LED_height
				print("[MazePosFinder] LED height of color ({0}, {1}, {2}) is updated" \
					.format(*color_bgr))

	def delete_target_color(self, color_bgr, color_type: ColorType):
		"""Delete the target color from the MazePositionFinder._colors_to_find

		@param color_bgr Specify the color to be removed in BGR domain
		@param color_type Specify the type of the color
		"""
		if self._recognition_thread.is_running:
			print("[MazePosFinder] Cannot update colors while recognizing.")
			return

		if color_type == ColorType.MAZE_UPPER_PLANE:
			self._upper_plane_color = None
			print("[MazePosFinder] Delete the color of upper plane")
		elif color_type == ColorType.MAZE_LOWER_PLANE:
			self._lower_plane_color = None
			print("[MazePosFinder] Delete the color of lower plane")
		else:
			where = -1
			try:
				where = self._colors_to_find.index(CarPosition(color_bgr, 0))
			except ValueError:
				print("[MazePosFinder] Color ({0}, {1}, {2}) is not existing" \
					.format(*color_bgr))
			else:
				self._colors_to_find.remove(where)
				print("[MazePosFinder] Color ({0}, {1}, {2}) is removed" \
					.format(*color_bgr))

	def recognize_maze(self):
		"""Recognize the position of the maze and generate the transform matrix

		The method uses MazePositionFinder._upper_plane_color and
		MazePositionFinder._lower_plane_color to get the position from the
		corresponding ColrPositionFinder. Then, invoke
		MazeManager._generate_transform_matrix() to generate the transform matrix
		of upper plane and lower plane. The result will be stored in both
		MazePositionFinder._upper_transform_mat and MazePositionFinder._lower_transform_mat.
		This method will wait until both transform matrixes are generated.
		"""
		if self._upper_plane_color is None or self._lower_plane_color is None:
			print("[MazePositionFinder] The color of the upper plane or the lower plane " \
				"has not been specified yet.")
			return

		self._upper_transform_mat = None
		self._lower_transform_mat = None

		# Generate transform matrix of the upper plane
		while self._upper_transform_mat is None:
			corner_poses = self._maze_color_pos_finder \
				.get_target_color(*self._upper_plane_color).pixel_position
			self._upper_transform_mat = \
				self._generate_transform_matrix(corner_poses)
		print("[MazePositionFinder] Transform matrix of the upper plane is generated.")

		# Generate transform matrix of the lower plane
		while self._lower_transform_mat is None:
			corner_poses = self._maze_color_pos_finder \
				.get_target_color(*self._lower_plane_color).pixel_position
			self._lower_transform_mat = \
				self._generate_transform_matrix(corner_poses)
		print("[MazePositionFinder] Transform matrix of the lower plane is generated.")

	def _generate_transform_matrix(self, corner_pos_4: list):
		"""Get a transform matrix which converts coordinates in the video stream
		to coordinates in the maze

		In the method, corner_pos_4 is sorted into the order of:
		left-bottom, right-bottom, left-top, and right-top.
		Then, map the sorted corner_pos_4 to (0, 0), (x of maze scale, 0),
		(0, y of maze scale), and (x of maze scale, y of maze scale) to
		generate the transform matrix. The maze scale is MazeManager._maze_scale.

		@param corner_pos_4 The list of Point2D that stores
		       the coordinates of 4 corners of the maze in the video stream
		@return A matrix that could transform the points from the
		        video stream coordinate to the maze coordinate
		"""
		if len(corner_pos_4) != 4:
			return None

		# Sort the input coordinate to the order of
		# (0, 0), (x, 0), (0, y), (x, y), The origin is set to left-bottom corner.
		corner_pos_4.sort(key = attrgetter('y'), reverse = True)
		if corner_pos_4[0].x > corner_pos_4[1].x:
			corner_pos_4[0], corner_pos_4[1] = \
				corner_pos_4[1], corner_pos_4[0]
		if corner_pos_4[2].x > corner_pos_4[3].x:
			corner_pos_4[2], corner_pos_4[3] = \
				corner_pos_4[3], corner_pos_4[2]

		from_coordinate = np.float32([ \
			list(corner_pos_4[0]), \
			list(corner_pos_4[1]), \
			list(corner_pos_4[2]), \
			list(corner_pos_4[3]) ])
		to_coordinate = np.float32([ \
			[0, 0], \
			[self._maze_scale.x, 0], \
			[0, self._maze_scale.y], \
			[self._maze_scale.x, self._maze_scale.y] ])

		return cv2.getPerspectiveTransform(from_coordinate, to_coordinate)

	def _generate_ratio_to_wall_height(self):
		"""Generate ratio to of the LED height to the maze wall height for all colors

		The result will be stored to MazePositionFinder._ratio_to_wall_height_array
		"""
		self._ratio_to_wall_height_array.clear()
		for i in range(len(self._colors_to_find)):
			self._ratio_to_wall_height_array \
				.append(self._colors_to_find[i].LED_height / self._wall_height)

	def start_recognize_car_pos(self):
		# Generate an array og the ratio of the LED height to the maze height
		# of all colors
		self._generate_ratio_to_wall_height()
		self._recognition_thread.start()

	def stop_recognize_car_pos(self):
		self._recognition_thread.stop()

	def _recognize_pos_in_maze(self):
		"""Recognize the position in the maze in the maze coordinate

		The method will calculate the position of the maze car whose LED color is
		stored at MazePositionFinder._colors_to_find.
		Get the pixel position found in the video stream from corresponding
		ColorPositionFinder by the LED color, and then calculate the car position
		by MazePositionFinder._recognize_position_in_maze._get_pos().
		The result is stored in CarPosition.postion.
		"""
		def _get_pos(pos_in_frame, ratio_to_wall_height) -> Point2D:
			""" Transform the pixel position to the maze coordinate

			First, transfrom the pixel position by MazePositionFinder._upper_transform_mat
			for upper plane (wall level), and MazePositionFinder._lower_transform_mat
			for lower plane (groud level). It will generate two coordinates,
			pos_upper_plane and pos_lower_plane.
			Then, get the maze coordinate by interploting these two coordinates.
			The formula is:
			pos_lower_plane + (pos_upper_plane - pos_lower_plane) * ratio_to_wall_height.

			@param pos_in_frame Specify the position found in the video stream
			@param ratio_to_wall_height Specify the ratio of the LED height to the wall
			       height
			@return A Point2D object that stores the maze position in integer
			"""
			pos = np.array([[[pos_in_frame.x, pos_in_frame.y]]], dtype = np.float32)
			pos_upper_plane = cv2.perspectiveTransform(pos, self._upper_transform_mat)
			pos_lower_plane = cv2.perspectiveTransform(pos, self._lower_transform_mat)
			pos_in_maze = pos_lower_plane + \
				(pos_upper_plane - pos_lower_plane) * ratio_to_wall_height
			return Point2D(int(round(pos_in_maze[0][0][0])), \
				int(round(pos_in_maze[0][0][1])))

		# Calculate the maze position for each color
		car_pos = []
		for i in range(len(self._colors_to_find)):
			target_color_pos = self._color_pos_finder \
				.get_target_color(*(self._colors_to_find[i].color_bgr))

			# Hope that there is only one position found in the video stream
			if len(target_color_pos.pixel_position) > 0:
				car_pos.append(_get_pos(target_color_pos.pixel_position[0], \
					self._ratio_to_wall_height_array[i]))
			# If there is no position found in the video stream,
			# remain the last result
			else:
				car_pos.append(self._colors_to_find[i].position)

		# Update the result
		self._colors_to_find_lock.acquire()
		for i in range(len(car_pos)):
			self._colors_to_find[i].position = car_pos[i]
		self._colors_to_find_lock.release()


class MazeManager:
	"""Manage the maze information and MazePositionFinders of team A and B

	@var _maze_position_finders The container for MazePositionFinders
	"""

	def __init__(self, color_pos_finders: ColorPosFinderHolder):
		"""Constructor

		@param color_pos_finders The instance of class ColorPosFinderHolder
		"""
		maze_color_finder = color_pos_finders.get_posFinder_by_type(ColorType.MAZE_LOWER_PLANE)
		team_a_color_finder = color_pos_finders.get_posFinder_by_type(ColorType.MAZE_CAR_TEAM_A)
		team_b_color_finder = color_pos_finders.get_posFinder_by_type(ColorType.MAZE_CAR_TEAM_B)
		self._maze_pos_finders = {
			'team A': MazePositionFinder(maze_color_finder, team_a_color_finder),
			'team B': MazePositionFinder(maze_color_finder, team_b_color_finder)}

	def set_maze(self, scale_x, scale_y, wall_height):
		"""Set the information of the maze to each MazePositionFinder

		@param scale_x The x scale of the maze
		@param scale_y The y scale of the maze
		@param wall_height The height of the maze wall
		"""
		for maze_pos_finder in self._maze_pos_finders.values():
			maze_pos_finder.set_maze(scale_x, scale_y, wall_height)

	def set_color(self, color_bgr, \
		old_color_type: ColorType, new_color_type: ColorType, LED_height = 0.0):
		"""Set the target color to the corresponding MazePositionFinder

		This method is similar to ColorManagerWidger._update_color.

		@param color_bgr The target color in BGR domain
		@param old_color_type The previous color type of the target color
		@param new_color_type The new color type of the target color
		@param LED_height The height of the LED on the maze car
		"""
		if new_color_type == ColorType.MAZE_LOWER_PLANE or \
			new_color_type == ColorType.MAZE_UPPER_PLANE:
			for maze_pos_finder in self._maze_pos_finders.values():
				maze_pos_finder.add_target_color(color_bgr, new_color_type)
		elif new_color_type == ColorType.MAZE_CAR_TEAM_A:
			self._maze_pos_finders['team A'] \
				.add_target_color(color_bgr, new_color_type, LED_height)
		elif new_color_type == ColorType.MAZE_CAR_TEAM_B:
			self._maze_pos_finders['team B'] \
				.add_target_color(color_bgr, new_color_type, LED_height)

		if old_color_type == ColorType.MAZE_LOWER_PLANE or \
			old_color_type == ColorType.MAZE_UPPER_PLANE:
			for maze_pos_finder in self._maze_pos_finders.values():
				maze_pos_finder.delete_target_color(color_bgr, old_color_type)
		elif old_color_type == ColorType.MAZE_CAR_TEAM_A:
			self._maze_pos_finders['team A'] \
				.delete_target_color(color_bgr, old_color_type)
		elif old_color_type == ColorType.MAZE_CAR_TEAM_B:
			self._maze_pos_finders['team B'] \
				.delete_target_color(color_bgr, old_color_type)

	def recognize_maze(self):
		"""Make every MazePositionFinder to recognize the maze
		"""
		for maze_pos_finder in self._maze_pos_finders.values():
			maze_pos_finder.recognize_maze()

	def start_recognize_car_pos(self):
		for maze_pos_finder in self._maze_pos_finders.values():
			maze_pos_finder.start_recognize_car_pos()

	def stop_recognize_car_pos(self):
		for maze_pos_finder in self._maze_pos_finders.values():
			maze_pos_finder.stop_recognize_car_pos()