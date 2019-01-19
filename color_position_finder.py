"""@package docstring
Find the position of the specified color in the image.
"""

import cv2
import imutils
import numpy as np
import logging
from threading import Lock
from util.job_thread import JobThread

from point import Point2D
from color_type import *

class ColorPosition:
	"""Data structure storing the position of the color found in the frame

	@param color_bgr Specify the target color in BGR domain
	       The color specified will be automatically converted into HSV domain.

	@var color_bgr The target color in BGR domain: [b, g, r]
	@var color_hsv The target color in HSV domain: [h, s, v]
	@var pixel_position A list of positions in pixel of the target color
	"""
	def __init__(self, color_bgr):
		self.color_bgr = color_bgr
		self.color_hsv = cv2.cvtColor(np.uint8([[color_bgr]]), cv2.COLOR_BGR2HSV)
		# cvtColor will return [pixel.y][pixel.x][hsv]
		self.color_hsv = self.color_hsv[0][0]
		self.pixel_position = []

	def __eq__(self, other):
		"""Predefined equal comparsion method

		Two ColorPosition objects are the same if their ColorPosition.color_bgr
		is the same.
		It is useful that you can get the ColorPosition element from a list
		by specifing the color (e.g., with statement
		list.index(ColorPosition([255, 0, 0]), you will get the element whose
		target color is blue).

		@return True if the color is the same
		"""
		return self.color_bgr == other.color_bgr

	def __ne__(self, other):
		return not __eq__(other)

	def copy(self):
		"""Return a clone of itself

		@return A clone of the ColorPosition object
		"""
		new_item = ColorPosition(self.color_bgr.copy())
		new_item.color_hsv = self.color_hsv.copy()
		new_item.pixel_position = self.pixel_position.copy()
		return new_item

class ColorPositionFinder:
	"""Find the given colors in the video stream of the camera

	@var _colors_to_find A list stores colors to be find in the frame
	@var _finder_name The name of the finder
	@var _camera The camera object for getting frames
	@var _color_finding_thread The thread for finding colors in the frame
	@var _colors_to_find_lock The read lock of _colors_to_find
	"""

	def __init__(self, finder_name, camera, fps = 100):
		"""Constructor

		@param finder_name The name of the finder
		@param camera Spcify the camera object
		@param fps Sepcify the updating rate of the car position
		"""
		self._logger = logging.getLogger(self.__class__.__name__)

		self._colors_to_find = []
		self._finder_name = finder_name
		self._camera = camera

		self._color_recognition_thread = JobThread(self._find_colors, \
			"Color_{0}".format(finder_name), 1.0 / fps)
		self._colors_to_find_lock = Lock()

		self._logger.debug("Finder \"{0}\" is run in fps {1}." \
			.format(finder_name, fps))

	def add_target_color(self, color_b, color_g, color_r):
		"""Add new target color to ColorPositionFinder._colors_to_find

		@param color_b The blue channel of the target color
		@param color_g The green channel of the target color
		@param color_r The red channel of the target color
		"""
		if self._color_recognition_thread.is_running:
			self._logger.error("Cannot add colors while recognizing.")
			return

		self._colors_to_find.append(ColorPosition([color_b, color_g, color_r]))
		self._logger.info("New target color ({0}, {1}, {2}) " \
			"is added to the finder \"{3}\"." \
			.format(color_b, color_g, color_r, self._finder_name))

	def delete_target_color(self, color_b, color_g, color_r):
		"""Delete the specified color from ColorPositionFinder._colors_to_find

		If the specified color is not in the _colors_to_find, the method
		will warn the user.

		@param color_b The blue channel of the target color
		@param color_g The green channel of the target color
		@param color_r The red channel of the target color
		"""
		if self._color_recognition_thread.is_running:
			self._logger.error("Cannot delete colors while recognizing.")
			return

		where = -1
		try:
			where = self._colors_to_find.index( \
				ColorPosition([color_b, color_g, color_r]))
		except ValueError:
			self._logger.error("Cannot delete color ({0}, {1}, {2}). " \
				"It is not in the finder \"{3}\"." \
				.format(color_b, color_g, color_r, self._finder_name))
		else:
			self._colors_to_find.remove(self._colors_to_find[where])
			self._logger.info("Target color ({0}, {1}, {2}) is deleted " \
				"from the finder \"{3}\"." \
				.format(color_b, color_g, color_r, self._finder_name))

	def get_target_color(self, color_b, color_g, color_r) -> ColorPosition:
		"""Get the copy of the element of the specified color in _colors_to_find

		If the specified color is not in the _colors_to_find, the method
		will warn the user.

		@param color_b The blue channel of the target color
		@param color_g The green channel of the target color
		@param color_r The red channel of the target color

		@return A copy of ColorPosition object in the _colors_to_find if the
		        specified color is existing
		"""
		where = -1
		new_item = None
		try:
			where = self._colors_to_find.index( \
				ColorPosition([color_b, color_g, color_r]))
		except ValueError:
			self._logger.error("Color ({0}, {1}, {2}) is not in the finder \"{3}\"." \
				.format(color_b, color_g, color_r, self._finder_name))
			return None
		else:
			self._colors_to_find_lock.acquire()
			new_item = self._colors_to_find[where].copy()
			self._colors_to_find_lock.release()
			return new_item

	def get_all_target_colors(self) -> list:
		"""Get a copy of all the target colors and their recognition result

		@return A copy of ColorPositionFinder._colors_to_find
		"""
		copied = []
		self._colors_to_find_lock.acquire()
		for i in range(len(self._colors_to_find)):
			copied.append(self._colors_to_find[i].copy())
		self._colors_to_find_lock.release()
		return copied

	def start_recognition(self):
		"""Start a new thread to do color recognition

		If the color recognition thread has been started,
		the method will do nothing.
		"""
		self._color_recognition_thread.start()

	def stop_recognition(self):
		"""Stop the color recognition thread

		If the color recognition thread has been stopped,
		the method will do nothing.
		"""
		self._color_recognition_thread.stop()

	def is_recognition_thread_started(self) -> bool:
		"""Is the color recognition thread has been started?

		@return True if the color recognition thread is started,
		        otherwise, return False.
		"""
		return self._color_recognition_thread.is_running

	def _find_colors(self):
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

		frame = self._camera.get_frame()
		frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		# TODO Create multiple thread to find colors if there are
		# too many colors to be found
		posFound = []
		for i in range(len(self._colors_to_find)):
			posFound.append(_find_target_color(frame_hsv, \
				self._colors_to_find[i].color_hsv))

		# Write local result back to the shared data
		self._colors_to_find_lock.acquire()
		for i in range(len(posFound)):
			self._colors_to_find[i].pixel_position = posFound[i].copy()
		self._colors_to_find_lock.release()

class ColorPosManager:
	"""Manage the ColorPositionFinders and provide accessing interface.

	@var _color_pos_finders A dict contains name-ColorPositionFinder pairs
	"""

	def __init__(self, camera, fps = 100):
		"""Constructor

		@param camera Specify the WebCam object
		@param fps Specify the updating rate of the car position
		"""
		self._is_recognition_started = False
		self._color_pos_finders = {
			PosFinderType.CAR_TEAM_A: ColorPositionFinder("team_A", camera, fps),
			PosFinderType.CAR_TEAM_B: ColorPositionFinder("team_B", camera, fps)
		}

	@property
	def is_recognition_started(self):
		return self._is_recognition_started

	def get_finder(self, finder_type: PosFinderType) -> ColorPositionFinder:
		"""Get the ColorPositionFinder by the PosFinderType

		@param finder_type One of PosFinderType
		@return The corresponding ColorPositionFinder
		"""
		return self._color_pos_finders[finder_type]

	def set_color(self, color_bgr, old_type: ColorType, new_type: ColorType):
		"""Set the color to the specific ColorPositionFinder accroding to its ColorType

		@param color_bgr Specify the target color in BGR domain
		@param old_type Specify the previous type of the color_bgr
		@param new_type Specify the new type of the color_bgr
		"""
		old_finder = PosFinderType.get_finder_type(old_type)
		new_finder = PosFinderType.get_finder_type(new_type)

		if old_finder == new_finder:
			return
		if old_finder is not None:
			self._color_pos_finders[old_finder].delete_target_color(*color_bgr)
		if new_finder is not None:
			self._color_pos_finders[new_finder].add_target_color(*color_bgr)

	def start_recognition(self):
		"""Start the recognition thread of the ColorPositionFinders of car colors
		"""
		for finder_type in self._color_pos_finders.keys():
			self._color_pos_finders[finder_type].start_recognition()
		self._is_recognition_started = True

	def stop_recognition(self):
		"""Stop the recognition thread of the ColorPositionFinders of car colors
		"""
		for finder_type in self._color_pos_finders.keys():
			self._color_pos_finders[finder_type].stop_recognition()
		self._is_recognition_started = False
