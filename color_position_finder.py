"""@package docstring
Find the position of the specified color in the image.
"""

import cv2

class ColorPosition:
	"""Data structure storing the position of the color found in the frame

	@var color The target color
	@var is_found Is this color found in the frame?
	@var pixel_position The position in pixel in the frame
	"""

	def __init__(self, color = None):
		self.color = color
		self.is_found = False
		self.pixel_position = [0, 0]

class ColorPositionFinder:
	"""Find the given colors in the video stream of the camera

	@var colors_to_find A list stores colors to be find in the frame
	@var camera The camera object for getting frames
	@var _frame Store the frame got from the camera
	"""

	def __init__(self, camera):
		"""Constructor

		@param camera Spcify the camera object
		"""
		self.colors_to_find = []
		self.camera = camera
		self._frame = None

	def select_colors(self):
		"""Select colors to be find in the frame

		The method will pop up a window showing the stream from the camera
		for the user to select colors.
		Use left mouse click to specify the color and press 'q' to confirm
		the selection and close the window.
		"""
		windowName = "Select target color (q to quit)"
		self._frame = self.camera.get_frame()
		cv2.namedWindow(windowName)
		cv2.setMouseCallback(windowName, self._on_mouse_click)

		while True:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

			self._frame = self.camera.get_frame()
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
