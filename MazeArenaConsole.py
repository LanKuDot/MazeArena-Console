"""
The main file of the maze car game server.
"""
# from web_camera import WebCamera
from application_gui import ApplicationGUI
from webcam import WebCamera

import cv2

if __name__ == "__main__":
	camera = WebCamera(src = 0, width = 1080, height = 720)

	camera.start_camera_thread()

	gui = ApplicationGUI(camera).start_gui()

	camera.stop_camera_thread()
