"""@package docstring
Find the position of the specified color in the image.
"""

import cv2
import imutils
import numpy as np

class ColorPosition:
	"""Data structure storing the position of the color found in the frame

	@param color_rgb Specify the target color in RGB domain
	       The color specified will be automatically converted into HSV domain.
	@var color_rgb The target color in RGB domain
	@var color_hsv The target color in HSV domain
	@var is_found Is this color found in the frame?
	@var pixel_position The position in pixel in the frame
	"""

	def __init__(self, color_rgb = None):
		self.color_rgb = color_rgb
		self.color_hsv = cv2.cvtColor(np.uint8([[color_rgb]]), cv2.COLOR_BGR2HSV)
		# cvtColor will return [pixel.y][pixel.x][hsv]
		self.color_hsv = self.color_hsv[0][0]
		self.is_found = False
		self.pixel_position = [0, 0]

class ColorPositionFinder:
	"""Find the given colors in the video stream of the camera

	@var colors_to_find A list stores colors to be find in the frame
	@var _camera The camera object for getting frames
	@var _frame Store the frame got from the camera
	"""

	def __init__(self, camera):
		"""Constructor

		@param camera Spcify the camera object
		"""
		self.colors_to_find = []
		self._camera = camera
		self._frame = None

	def select_colors(self):
		"""Select colors to be find in the frame

		The method will pop up a window showing the stream from the camera
		for the user to select colors.
		Use left mouse click to specify the color and press 'q' to confirm
		the selection and close the window.
		"""
		windowName = "Select target color (q to quit)"
		self._frame = self._camera.get_frame()
		cv2.namedWindow(windowName)
		cv2.setMouseCallback(windowName, self._on_mouse_click)

		while True:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

			self._frame = self._camera.get_frame()

			if len(self.colors_to_find) > 0:
				self.find_colors()

			cv2.imshow(windowName, self._frame)

		cv2.destroyWindow(windowName)

	def _on_mouse_click(self, event, x, y, flags, param):
		"""The callback function of the mouse clicking event

		When the left mouse click releases, store the color at where
		the mouse point is in the frame to ColorPositionFinder.colors_to_find.
		"""
		if event == cv2.EVENT_LBUTTONUP:
			self.add_target_color( \
				self._frame[y, x][0], self._frame[y, x][1], self._frame[y, x][2])

	def add_target_color(self, color_r, color_g, color_b):
		"""Add new target color to ColorPositionFinder.colors_to_find

		@param color_r The red channel of the target color
		@param color_g The green channel of the target color
		@param color_b The blue channel of the target color
		"""
		self.colors_to_find.append(ColorPosition([color_r, color_g, color_b]))
		print("[ColorPositionFinder] New target color added:" \
			" ({0}, {1}, {2})".format(color_r, color_g, color_b))

	def find_colors(self):
		# Convert color from RGB domain from HSV domain
		frame_hsv = cv2.cvtColor(self._frame, cv2.COLOR_BGR2HSV)

		# Set the range of detecting colors in HSV domain
		hue = self.colors_to_find[0].color_hsv[0][0][0]
		# TODO The range of the detecting colors can be set on the UI
		low_hue = hue - 15 if hue - 15 > -1 else 0
		high_hue = hue + 15 if hue + 15 < 256 else 255
		lower_bound = np.array([low_hue, 100, 100], dtype = np.uint8)
		upper_bound = np.array([high_hue, 255, 255], dtype = np.uint8)

		# Only colors in defined range will be passed
		filtered_frame = cv2.inRange(frame_hsv, lower_bound, upper_bound)

		# Erode and dilate the filtered result with 7 x 7 kernal
		# to eliminate the noise
		kernal = np.ones((3, 3), dtype = np.uint8)
		filtered_frame = cv2.erode(filtered_frame, kernal, iterations = 1)
		filtered_frame = cv2.dilate(filtered_frame, kernal, iterations = 1)
		filtered_frame = cv2.GaussianBlur(filtered_frame, (5, 5), 0)

		# Find contours in the final filtered frame
		contours = cv2.findContours(filtered_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		contours = contours[0] if imutils.is_cv2() else contours[1]

		# Find center point of each contour
		centres = []
		for i in range(len(contours)):
			moments = cv2.moments(contours[i])
			centres.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))

		# Draw the dot found
		for i in range(len(centres)):
			cv2.circle(self._frame, centres[i], 5, (0, 0, 150), -1)

		#return self.colors_to_find
