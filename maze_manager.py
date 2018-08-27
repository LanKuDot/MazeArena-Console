"""@package docstring
The manager that handling the information of the maze,
such as the size of the maze, the position of the maze cars.
"""

import cv2
import numpy as np
from operator import attrgetter

from point import Point2D
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
	@var _upper_transform_mat A matrix that transform from the frame
	     coordinate to the coordinate of the upper plane of the maze
	@var _lower_transform_mat Similar to _upper_transform_mat, but is for
	     the lower plane of the maze
	"""

	def __init__(self, color_pos_finders: ColorPosFinderHolder):
		"""Constructor

		@param color_pos_finders The instance of class ColorPosFinderHolder
		"""
		self._color_pos_finders = color_pos_finders

		self._maze_scale = None
		self._wall_height = 0
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
		print('[MazeManager] Set maze scale: {0}, wall_height: {1}' \
			.format(self._maze_scale, self._wall_height))

