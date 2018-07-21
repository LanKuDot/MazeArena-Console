"""@package docstring
Find the position of the specified color in the image.
"""

import cv2
import imutils
import numpy as np
from enum import Enum
from threading import Thread, Lock

from point import Point2D

class ColorPosition:
	"""Data structure storing the position of the color found in the frame

	@param color_rgb Specify the target color in RGB domain
	       The color specified will be automatically converted into HSV domain.

	@var color_rgb The target color in RGB domain: [r, g, b]
	@var color_hsv The target color in HSV domain: [h, s, v]
	@var color_type The represenation of the color in the maze
	@var pixel_position A list of positions in pixel of the target color
	"""

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

	def __init__(self, color_rgb, color_type = Type.OTHER):
		self.color_rgb = color_rgb
		self.color_hsv = cv2.cvtColor(np.uint8([[color_rgb]]), cv2.COLOR_BGR2HSV)
		# cvtColor will return [pixel.y][pixel.x][hsv]
		self.color_hsv = self.color_hsv[0][0]
		self.color_type = color_type
		self.pixel_position = []

	def __eq__(self, other):
		"""Predefined equal comparsion method

		Two ColorPosition objects are the same if their ColorPosition.color_rgb
		is the same.
		It is useful that you can get the ColorPosition element from a list
		by specifing the color (e.g., with statement
		list.index(ColorPosition([255, 0, 0]), you will get the element whose
		target color is red).

		@return True if the color is the same
		"""
		return self.color_rgb == other.color_rgb

	def __ne__(self, other):
		return not __eq__(other)

	def copy(self):
		"""Return a clone of itself

		@return A clone of the ColorPosition object
		"""
		new_item = ColorPosition(self.color_rgb.copy(), self.color_type)
		new_item.color_hsv = self.color_hsv.copy()
		new_item.pixel_position = self.pixel_position.copy()
		return new_item

class ColorPositionFinder:
	"""Find the given colors in the video stream of the camera

	@var _colors_to_find A list stores colors to be find in the frame
	@var _camera The camera object for getting frames
	@var _frame Store the frame got from the camera
	@var _color_finding_thread The thread for finding colors in the frame
	@var _is_thread_started Is the _color_finding_thread started?
	@var _colors_to_find_lock The read lock of _colors_to_find
	"""

	def __init__(self, camera):
		"""Constructor

		@param camera Spcify the camera object
		"""
		self._colors_to_find = []
		self._camera = camera
		self._frame = None

		self._color_finding_thread = None
		self._is_thread_started = False
		self._colors_to_find_lock = Lock()

	def add_target_color(self, color_r, color_g, color_b):
		"""Add new target color to ColorPositionFinder._colors_to_find

		@param color_r The red channel of the target color
		@param color_g The green channel of the target color
		@param color_b The blue channel of the target color
		"""
		self._colors_to_find.append(ColorPosition([color_r, color_g, color_b]))
		print("[ColorPositionFinder] New target color added:" \
			" ({0}, {1}, {2})".format(color_r, color_g, color_b))

	def delete_target_color(self, color_r, color_g, color_b):
		"""Delete the specified color from ColorPositionFinder._colors_to_find

		If the specified color is not in the _colors_to_find, the method
		will warn the user.

		@param color_r The red channel of the target color
		@param color_g The green channel of the target color
		@param color_b The blue channel of the target color
		"""
		where = -1
		try:
			where = self._colors_to_find.index( \
				ColorPosition([color_r, color_g, color_b]))
		except ValueError:
			print("[ColorPositionFinder] Color ({0}, {1}, {2}) " \
				"is not in the target colors".format(color_r, color_g, color_b))
		else:
			self._colors_to_find.remove(where)
			print("[ColorPositionFinder] Target color removed:" \
			" ({0}, {1}, {2})".format(color_r, color_g, color_b))

	def get_target_color(self, color_r, color_g, color_b) -> ColorPosition:
		"""Get the copy of the element of the specified color in _colors_to_find

		If the specified color is not in the _colors_to_find, the method
		will warn the user.

		@param color_r The red channel of the target color
		@param color_g The green channel of the target color
		@param color_b The blue channel of the target color

		@return A copy of ColorPosition object in the _colors_to_find if the
		        specified color is existing
		"""
		where = -1
		new_item = None
		try:
			where = self._colors_to_find.index( \
				ColorPosition([color_r, color_g, color_b]))
		except ValueError:
			print("[ColorPositionFinder] Color ({0}, {1}, {2}) " \
				"is not in the target colors".format(color_r, color_g, color_b))
		else:
			new_item = self._colors_to_find[where].copy()
			return new_item

	def find_colors(self):
		def _get_detect_range(color_hsv):
			"""Generate the detecting color range from predefined sensitivity

			@param color_hsv The detecting colot in HSV domain
			@return (lower_bound, upper_bound) The range of the detecting color
			"""
			# TODO The range of the detecting colors can be set on the UI
			hue = color_hsv[0]
			low_hue = hue - 15 if hue - 15 > -1 else 0
			high_hue = hue + 15 if hue + 15 < 256 else 255
			lower_bound = np.array([low_hue, 100, 180], dtype = np.uint8)
			upper_bound = np.array([high_hue, 255, 255], dtype = np.uint8)
			return lower_bound, upper_bound

		def _find_target_color(target_frame_hsv, target_color_hsv):
			"""Find the position of the specified color in the given frame

			@param target_frame_hsv The source frame in HSV domain
			@param target_color_hsv The color in the HSV domain to be found
			       in the target_frame_hsv
			@return A list of positions in pixel where the target color is at
			        It is possible that returning an empty list
			"""
			lower_bound, upper_bound = _get_detect_range(target_color_hsv)
			# Only colors in defined range will be passed
			filtered_frame = cv2.inRange(target_frame_hsv, lower_bound, upper_bound)

			# Erode and dilate the filtered result with 3 x 3 kernal
			# to eliminate the noise
			kernal = np.ones((3, 3), dtype = np.uint8)
			filtered_frame = cv2.erode(filtered_frame, kernal, iterations = 1)
			filtered_frame = cv2.dilate(filtered_frame, kernal, iterations = 1)
			filtered_frame = cv2.GaussianBlur(filtered_frame, (5, 5), 0)

			# Find contours in the final filtered frame
			contours = cv2.findContours(filtered_frame, \
				cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			contours = contours[0] if imutils.is_cv2() else contours[1]

			# Find center point of each contour
			centres = []
			for i in range(len(contours)):
				moments = cv2.moments(contours[i])
				centres.append(Point2D(int(moments['m10']/moments['m00']), \
					int(moments['m01']/moments['m00'])))
			return centres

		frame_hsv = cv2.cvtColor(self._frame, cv2.COLOR_BGR2HSV)
		# TODO Create multiple thread to find colors if there are
		# too many colors to be found
		for i in range(len(self._colors_to_find)):
			posFound = _find_target_color(frame_hsv, self._colors_to_find[i].color_hsv)
			self._colors_to_find[i].pixel_position = posFound.copy()

	def _mark_searching_result(self):
		"""Mark the searching result to the original frame

		The method will take the positions stored in the
		ColorPosition.pixel_position from each color stored in the
		ColorPositionFinder._colors_to_find.
		And then mark red dots at these position.
		"""
		for color_id in range(len(self._colors_to_find)):
			posFound = self._colors_to_find[color_id].pixel_position
			for i in range(len(posFound)):
				cv2.circle(self._frame, (posFound[i].x, posFound[i].y), \
					5, (0, 0, 150), -1)
