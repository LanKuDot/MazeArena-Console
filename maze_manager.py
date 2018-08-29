"""@package docstring
The manager that handling the information of the maze,
such as the size of the maze, the position of the maze cars.
"""

import cv2
import numpy as np
from operator import attrgetter

from point import Point2D
from color_type import ColorType
from color_position_finder import *

class CarPosition:
	"""A data structure for the position of the maze car in the maze

	@var color_bgr The LED color of the maze car in BGR domain
	@var car_height The height of the LED on the maze car
	@var ratio_to_wall_height The ratio of the car height to the wall height
	@var position The position of the maze car in the maze
	"""

	def __init__(self, color_bgr, car_height):
		"""Constructor

		@param color_bgr Specify the color of the LED on the maze car
		@param car_height Specify the height of the LED on the maze car
		"""
		self.color_bgr = color_bgr
		self.car_height = car_height
		self.ratio_to_wall_height = 1.0
		self.position = None

	def __eq__(self, other):
		"""Predefined equal comparsion method

		Two CarPosition objects are the same if their ColorPosition.color_bgr
		is the same.

		@return True if the color is the same
		"""
		return self.color_bgr == other.color_bgr

	def __ne__(self, other):
		return not self.__eq__(other)

class MazeManager:
	"""

	@var _color_pos_finders The ColorPositionFinders for getting the position
	     of colors found in the video stream
	@var _maze_scale A Point2D(x, y) which represents the coordinate scale of
	     the maze (0 ~ x, 0 ~ y)
	@var _wall_height The height of the maze wall
	@var _upper_plane_color The color that locates the upper plane of the maze
	@var _lower_plane_color Simliar to _upper_plane_color but for the lower plane
	@var _upper_transform_mat A matrix that transform from the frame
	     coordinate to the coordinate of the upper plane of the maze
	@var _lower_transform_mat Similar to _upper_transform_mat, but for
	     the lower plane of the maze
	"""

	def __init__(self, color_pos_finders: ColorPosFinderHolder):
		"""Constructor

		@param color_pos_finders The instance of class ColorPosFinderHolder
		"""
		self._color_pos_finders = color_pos_finders

		self._maze_scale = None
		self._wall_height = 0
		self._upper_plane_color = None
		self._lower_plane_color = None
		self._upper_transform_mat = None
		self._lower_transform_mat = None

	def set_maze(self, scale_x, scale_y, wall_height):
		"""Set the information of the maze

		@param scale_x The x scale of the maze
		@param scale_y The y scale of the maze
		@param wall_height The height of the maze wall
		"""
		self._maze_scale = Point2D(scale_x, scale_y)
		self._wall_height = wall_height

	def set_color(self, color_bgr, \
		old_color_type: ColorType, new_color_type: ColorType):
		"""Set the target color in the maze

		This method is similar to ColorManagerWidger._update_color_finder.

		@param color_bgr The target color in BGR domain
		@param old_color_type The previous color type of the target color
		@param new_color_type The new color type of the target color
		"""
		if new_color_type == ColorType.MAZE_UPPER_PLANE:
			self._upper_plane_color = color_bgr
		elif new_color_type == ColorType.MAZE_LOWER_PLANE:
			self._lower_plane_color = color_bgr

	def recognize_maze(self):
		if self._upper_plane_color == None or self._lower_plane_color == None:
			print("[MazeManager] The color of the upper plane or the lower plane " \
				"has not been specified yet.")
			return

		color_finder_of_maze: ColorPositionFinder = \
			self._color_pos_finders.get_posFinder_by_type(ColorType.MAZE_UPPER_PLANE)
		self._upper_transform_mat = None
		self._lower_transform_mat = None

		# Generate transform matrix of the upper plane
		while self._upper_transform_mat is None:
			corner_poses = color_finder_of_maze \
				.get_target_color(*self._upper_plane_color).pixel_position
			self._upper_transform_mat = \
				self._generate_transform_matrix(corner_poses)
		print("[MazeManager] Transform matrix of the upper plane is generated.")

		# Generate transform matrix of the lower plane
		while self._lower_transform_mat is None:
			corner_poses = color_finder_of_maze \
				.get_target_color(*self._lower_plane_color).pixel_position
			self._lower_transform_mat = \
				self._generate_transform_matrix(corner_poses)
		print("[MazeManager] Transform matrix of the lower plane is generated.")

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
		# (0, 0), (x, 0), (0, y), (x, y)
		corner_pos_4.sort(key = attrgetter('y'))
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
