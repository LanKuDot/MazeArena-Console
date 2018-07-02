"""
The main file of the maze car game server.
"""
# from web_camera import WebCamera
from application_gui import ApplicationGUI
from color_position_finder import ColorPositionFinder
from webcam import WebCamera

import cv2

if __name__ == "__main__":
	camera = WebCamera(width = 800, height = 600)
	camera.start_camera_thread()

	color_position_finder = ColorPositionFinder(camera)

	gui = ApplicationGUI(color_position_finder).start_gui()

	camera.stop_camera_thread()
