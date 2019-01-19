"""@package docstring
The manager that handling the information of the maze,
such as the size of the maze, the position of the maze cars.
"""

import cv2
import numpy as np
import logging
from operator import attrgetter
from threading import Lock

from point import Point2D
from color_type import *
from color_position_finder import *
from util.job_thread import JobThread

class MazePosition:
	"""A data structure for the position of the maze car in the maze

	@var color_bgr The LED color of the maze car in BGR domain
	@var LED_height The height of the LED on the maze car
	@var position The position of the maze car in the maze
	@var position_detail The detailed position of the maze car in the maze.
	     Always in 128 x 128 scale.
	@var _missing_counter The counter the counts the number of continous calls
	     that cannot find the maze position. This counter will be reset
		 if the maze position if found at a call. If the counter is more than
		 a certain value, than position and position_detail will be set to
		 (-1, -1) to mark that the maze car is not in the maze.
	"""

	def __init__(self, color_bgr, LED_height: float):
		"""Constructor

		@param color_bgr Specify the color of the LED on the maze car
		@param LED_height Specify the height of LED on the maze car
		"""
		self.color_bgr = color_bgr
		self.LED_height = LED_height
		self.position = Point2D(-1, -1)
		self.position_detail = Point2D(-1, -1)	# Always in 128 x 128 scale
		self._missing_counter = 0 # It will not be copied.

	def __eq__(self, other):
		"""Predefined equal comparsion method

		Two MazePosition objects are the same if their ColorPosition.color_bgr
		is the same.

		@return True if the color is the same
		"""
		return self.color_bgr == other.color_bgr

	def __ne__(self, other):
		return not self.__eq__(other)

	def copy(self):
		"""Return a clone of itself

		@return A clone of MazePosition object
		"""
		new_item = MazePosition(self.color_bgr.copy(), self.LED_height)
		# namedtuple cannot be modified
		new_item.position = self.position
		new_item.position_detail = self.position_detail
		return new_item

class MazePositionFinder:
	"""Find the position of the colors in the maze

	MazePositionFinder uses the position of the colors found in the video stream
	(which is from ColorPositionFinder) to find the position of the colors in
	the maze.

	@var _color_pos_finder The ColorPosFinder that contains the colors to be found
	     in the MazePositionFinder
	@var _finder_name The name of the finder
	@var _wall_height The height of the maze wall
	@var _upper_transform_mat A matrix that transform from the frame
	     coordinate to the coordinate of the upper plane of the maze
	@var _lower_transform_mat Similar to _upper_transform_mat, but for
	     the lower plane of the maze
	@var _colors_to_find A list of MazePosition
	@var _colors_to_find_lock A lock for accessing _colors_to_find
	@var _ratio_to_wall_height_array An array of the ratio of LED height to the
	     maze wall height of each color in _colors_to_find
	@var _max_missing_counter The maximum number of missing counter that will
	     treat this color as missing
	@var _recognition_thread A JobThread for recognizing the car position
	"""

	def __init__(self, finder_name, color_pos_finder: ColorPositionFinder, fps = 30):
		self._logger = logging.getLogger(self.__class__.__name__)
		self._finder_name = finder_name
		self._color_pos_finder = color_pos_finder

		self._wall_height = None
		self._upper_transform_mat = None
		self._lower_transform_mat = None
		self._upper_transform_mat_detail = None
		self._lower_transform_mat_detail = None
		self._colors_to_find = []
		self._colors_to_find_lock = Lock()
		self._ratio_to_wall_height_array = []

		try:
			if int(fps) < 1:
				raise ValueError
		except ValueError:
			self._logger.error("Invaild fps: {0}. Set to 30.".format(fps))
			fps = 30

		self._max_missing_counter = fps * 5	# 5 seconds

		self._recognition_thread = JobThread(self._recognize_pos_in_maze, \
			"Car_{0}".format(finder_name), 1.0 / fps)

		self._logger.debug("Finder {0} is run in fps {1}." \
			.format(finder_name, fps))

	def set_wall_height(self, wall_height):
		self._wall_height = wall_height

	def set_transform_matrix(self, upper_plane, lower_plane, \
		upper_plane_detail, lower_plane_detail):
		"""Set the information of the maze

		@param upper_plane Specify the transform matrix of the upper plane
		@param lower_plane Specify the transform matrix of the lower plane
		@param upper_plane_detail Specify the transform matrix of the upper plane
		       in the detailed scale
		@param lower_plane_detail Specify the transform matrix of the lower plane
		       in the detailed scale
		"""
		self._upper_transform_mat = upper_plane
		self._lower_transform_mat = lower_plane
		self._upper_transform_mat_detail = upper_plane_detail
		self._lower_transform_mat_detail = lower_plane_detail

	def add_target_color(self, color_bgr, LED_height = 0.0):
		"""Add a target color to the position finding list

		@param color_bgr The target color in BGR domain
		@param LED_height The height of the LED on the maze car
		"""
		if self._recognition_thread.is_running:
			self._logger.error("Cannot add colors while recognizing.")
			return

		try:
			where = self._colors_to_find.index(MazePosition(color_bgr, 0))
		except ValueError:
			self._colors_to_find.append(MazePosition(color_bgr, LED_height))
			self._logger.info("New target color ({0}, {1}, {2}) is added " \
				"to the finder \"{3}\"." \
				.format(*color_bgr, self._finder_name))
		else:
			self._colors_to_find[where].LED_height = LED_height
			self._logger.info("LED height of color ({0}, {1}, {2}) " \
				"in the finder \"{3}\" is updated." \
				.format(*color_bgr, self._finder_name))

	def delete_target_color(self, color_bgr):
		"""Delete the target color from the MazePositionFinder._colors_to_find

		@param color_bgr Specify the color to be removed in BGR domain
		"""
		if self._recognition_thread.is_running:
			self._logger.error("Cannot delete colors while recognizing.")
			return

		try:
			where = self._colors_to_find.index(MazePosition(color_bgr, 0))
		except ValueError:
			self._logger.error("Cannot delele color ({0}, {1}, {2}). " \
				"It is not in the finder \"{3}\"." \
				.format(*color_bgr, self._finder_name))
		else:
			self._colors_to_find.remove(self._colors_to_find[where])
			self._logger.info("Target color ({0}, {1}, {2}) is deleted " \
				"from the finder \"{3}\"." \
				.format(*color_bgr, self._finder_name))

	def get_maze_pos(self, color_bgr) -> MazePosition:
		"""Get the maze position of the specified color

		@param color_bgr Specify the color in BGR domain
		@return The copy MazePosition object of the specified color
		@retval None if the specicifed color is not found
		"""
		try:
			where = self._colors_to_find.index(MazePosition(color_bgr, 0))
		except ValueError:
			return None
		else:
			with self._colors_to_find_lock:
				return self._colors_to_find[where].copy()

	def get_all_maze_pos(self) -> list:
		"""Get a copy of all the target colors and their maze positions

		@return A copy of MazePositionFinder._colors_to_find
		"""
		target_colors = []
		with self._colors_to_find_lock:
			for i in range(len(self._colors_to_find)):
				target_colors.append(self._colors_to_find[i].copy())
		return target_colors

	def _generate_ratio_to_wall_height(self):
		"""Generate ratio to of the LED height to the maze wall height for all colors

		The result will be stored to MazePositionFinder._ratio_to_wall_height_array
		"""
		self._ratio_to_wall_height_array.clear()
		for i in range(len(self._colors_to_find)):
			self._ratio_to_wall_height_array \
				.append(self._colors_to_find[i].LED_height / self._wall_height)

	def start_recognition(self):
		# Generate an array og the ratio of the LED height to the maze height
		# of all colors
		if self._upper_transform_mat is None or self._lower_transform_mat is None:
			self._logger.error("The maze has not been recognized yet.")
			return

		self._generate_ratio_to_wall_height()
		self._recognition_thread.start()

	def stop_recognition(self):
		self._recognition_thread.stop()

	def _recognize_pos_in_maze(self):
		"""Recognize the position in the maze in the maze coordinate

		The method will calculate the position of the maze car whose LED color is
		stored at MazePositionFinder._colors_to_find.
		Get the pixel position found in the video stream from corresponding
		ColorPositionFinder by the LED color, and then calculate the car position
		by MazePositionFinder._recognize_position_in_maze._get_pos().
		The result is stored in MazePosition.postion.
		"""
		def _get_pos(pos_in_frame, ratio_to_wall_height, \
			upper_transform_mat, lower_transform_mat) -> Point2D:
			""" Transform the pixel position to the maze coordinate

			First, transfrom the pixel position by MazePositionFinder._upper_transform_mat
			for upper plane (wall level), and MazePositionFinder._lower_transform_mat
			for lower plane (groud level). It will generate two coordinates,
			pos_at_upper_plane and pos_at_lower_plane.
			Then, get the maze coordinate by interploting these two coordinates.
			The formula is:
			pos_at_lower_plane + (pos_at_upper_plane - pos_at_lower_plane)
			* ratio_to_wall_height.

			@param pos_in_frame Specify the position found in the video stream
			@param ratio_to_wall_height Specify the ratio of the LED height to the wall
			       height
			@param upper_transform_mat Specify the transform matrix of the upper plane
			@param lower_transform_mat Specify the transform matrix of the lower plane
			@return A Point2D object that stores the maze position in integer
			"""
			pos = np.array([[[pos_in_frame.x, pos_in_frame.y]]], dtype = np.float32)
			pos_at_upper_plane = cv2.perspectiveTransform(pos, upper_transform_mat)
			pos_at_lower_plane = cv2.perspectiveTransform(pos, lower_transform_mat)
			pos_in_maze = pos_at_lower_plane + \
				(pos_at_upper_plane - pos_at_lower_plane) * ratio_to_wall_height
			return Point2D(int(round(pos_in_maze[0][0][0] - 0.5)), \
				int(round(pos_in_maze[0][0][1] - 0.5)))

		# Calculate the maze position for each color
		car_pos = []
		car_pos_detail = []
		for i in range(len(self._colors_to_find)):
			target_color_pos = self._color_pos_finder \
				.get_target_color(*(self._colors_to_find[i].color_bgr))

			# Hope that there is only one position found in the video stream
			if len(target_color_pos.pixel_position) > 0:
				pos = _get_pos(target_color_pos.pixel_position[0], \
					self._ratio_to_wall_height_array[i], \
					self._upper_transform_mat, \
					self._lower_transform_mat)
				car_pos.append(pos)

				pos_detail = _get_pos(target_color_pos.pixel_position[0], \
					self._ratio_to_wall_height_array[i], \
					self._upper_transform_mat_detail, \
					self._lower_transform_mat_detail)
				car_pos_detail.append(pos_detail)
			# If there is no position found in the video stream,
			# return (-1, -1)
			else:
				car_pos.append(Point2D(-1, -1))
				car_pos_detail.append(Point2D(-1, -1))

		# Update the result
		with self._colors_to_find_lock:
			for i in range(len(car_pos)):
				if car_pos[i].x >= 0:
					# Position is found. Reset the counter
					self._colors_to_find[i].position = car_pos[i]
					self._colors_to_find[i].position_detail = car_pos_detail[i]
					self._colors_to_find[i]._missing_counter = 0
				elif self._colors_to_find[i]._missing_counter > self._max_missing_counter:
					# Position is missing for a while. Set to (-1, -1)
					self._colors_to_find[i].position = car_pos[i]
					self._colors_to_find[i].position_detail = car_pos_detail[i]
				else:
					# Position is missing. Increase the missing counter
					# and remain the lastest vaild position.
					self._colors_to_find[i]._missing_counter += 1

class MazeManager:
	"""Manage the maze information and MazePositionFinders of team A and B

	@var _maze_pos_finders The container for MazePositionFinders
	"""

	def __init__(self, color_pos_manager: ColorPosManager, fps = 30):
		"""Constructor

		@param color_pos_manager The instance of class ColorPosManager
		@param fps Specify the updating rate of the car position in maze
		"""
		team_a_color_finder = color_pos_manager.get_finder(PosFinderType.CAR_TEAM_A)
		team_b_color_finder = color_pos_manager.get_finder(PosFinderType.CAR_TEAM_B)
		self._maze_pos_finders = {
			PosFinderType.CAR_TEAM_A: MazePositionFinder("team_A", team_a_color_finder, fps),
			PosFinderType.CAR_TEAM_B: MazePositionFinder("team_B", team_b_color_finder, fps)
		}

	def recognize_maze(self, scale_x: int, scale_y: int, wall_height: float, \
		upper_corner: list, lower_corner: list):
		"""Generate the transform matries and set them to all MazePositionFinder

		@param scale_x The x scale of the maze
		@param scale_y The y scale of the maze
		@param wall_height The height of the maze wall
		@param upper_corner A list storing point2D of 4 corners on the upper plane
		@param lower_corner A list storing point2D of 4 corners on the lower plane
		"""
		maze_scale = Point2D(scale_x, scale_y)
		maze_scale_detail = Point2D(128, 128)
		upper_transform_mat = self._generate_transform_matrix(upper_corner, maze_scale)
		lower_transform_mat = self._generate_transform_matrix(lower_corner, maze_scale)
		upper_transform_mat_detail = \
			self._generate_transform_matrix(upper_corner, maze_scale_detail)
		lower_transform_mat_detail = \
			self._generate_transform_matrix(lower_corner, maze_scale_detail)

		for maze_pos_finder in self._maze_pos_finders.values():
			maze_pos_finder.set_transform_matrix(upper_transform_mat, lower_transform_mat, \
				upper_transform_mat_detail, lower_transform_mat_detail)
			maze_pos_finder.set_wall_height(wall_height)

	def _generate_transform_matrix(self, corner_pos_4: list, maze_scale: Point2D):
		"""Get a transform matrix which converts coordinates in the video stream
		to coordinates in the maze

		In the method, corner_pos_4 is sorted into the order of:
		left-bottom, right-bottom, left-top, and right-top.
		Then, map the sorted corner_pos_4 to (0, 0), (x of maze scale, 0),
		(0, y of maze scale), and (x of maze scale, y of maze scale) to
		generate the transform matrix. The maze scale is MazeManager._maze_scale.

		@param corner_pos_4 The list of Point2D that stores
		       the coordinates of 4 corners of the maze in the video stream
		@param maze_scale The subdivision of the maze, like 8 x 8.
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
			[maze_scale.x, 0], \
			[0, maze_scale.y], \
			[maze_scale.x, maze_scale.y] ])

		return cv2.getPerspectiveTransform(from_coordinate, to_coordinate)

	def set_color(self, color_bgr, \
		old_color_type: ColorType, new_color_type: ColorType, LED_height = 0.0):
		"""Set the target color to the corresponding MazePositionFinder

		This method is similar to ColorManagerWidger._update_color.

		@param color_bgr The target color in BGR domain
		@param old_color_type The previous color type of the target color
		@param new_color_type The new color type of the target color
		@param LED_height The height of the LED on the maze car
		"""
		old_finder_type = PosFinderType.get_finder_type(old_color_type)
		new_finder_type = PosFinderType.get_finder_type(new_color_type)

		if new_finder_type is not None:
			self._maze_pos_finders[new_finder_type] \
				.add_target_color(color_bgr, LED_height)

		if new_color_type == old_color_type:
			return

		if old_finder_type is not None:
			self._maze_pos_finders[old_finder_type].delete_target_color(color_bgr)

	def get_finder(self, finder_type: PosFinderType) -> MazePositionFinder:
		"""Get the MazePositionFinder by the type of the team

		@param finder_type Specify the type of the finder
		"""
		return self._maze_pos_finders[finder_type]

	def get_finder_by_name(self, name: str) -> MazePositionFinder:
		"""Get the MazePositionFinder by "A" or "B"
		"""
		return {
			"A": self.get_finder(PosFinderType.CAR_TEAM_A),
			"B": self.get_finder(PosFinderType.CAR_TEAM_B)
		}.get(name)

	def get_maze_pos(self, color_bgr, team: str) -> MazePosition:
		"""Get the position in the maze of the spcified maze car

		@param color_bgr Specify the LED color of the maze car in BGR domain
		@param team Specify the team of the maze car. Should be "A" or "B"
		@return The copy of MazePosition object of the specified color
		@retval None If the specified color in not found
		"""
		finder = self.get_finder_by_name(team)
		return finder.get_maze_pos(color_bgr)

	def get_team_maze_pos(self, team: str):
		"""Get the position of all the maze cars in a team

		@param team Specify the team of the maze cars. Should be "A" or "B"
		@return A list of MazePosition objects of the specfied team
		"""
		finder = self.get_finder_by_name(team)
		return finder.get_all_maze_pos()

	def start_recognition(self):
		for maze_pos_finder in self._maze_pos_finders.values():
			maze_pos_finder.start_recognition()

	def stop_recognition(self):
		for maze_pos_finder in self._maze_pos_finders.values():
			maze_pos_finder.stop_recognition()