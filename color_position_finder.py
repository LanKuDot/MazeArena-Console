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
	"""

	def __init__(self, camera):
		"""Constructor

		@param camera Spcify the camera object
		"""
		self.colors_to_find = []
		self.camera = camera

	def select_colors(self):
		"""Select colors to be find in the frame

		The method will pop up a window showing the stream from the camera
		for the user to select colors.
		Use left mouse click to specify the color and press 'q' to confirm
		the selection and close the window.
		"""
		windowName = "Select target color (q to quit)"
		cv2.namedWindow(windowName)

		while True:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

			frame = self.camera.get_frame()
			cv2.imshow(windowName, frame)

		cv2.destroyWindow(windowName)
