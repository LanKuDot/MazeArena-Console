"""@package docstring
Capture frames from the web camera.
"""

from threading import Thread, Lock
import cv2

class WebCamera:
	"""Capture frames from the web camera.

	It will create a new thread to get frames from the web camera.
	The camera thread has to be started first by invoking
	WebCamera.start_camera_thread, and then accessing frames captured
	by invoking WebCamera.get_frame.

	Note that if you want to access WebCamera.isCaptured and
	WebCamera.frame from another thread, you have to check the
	WebCamera.read_lock first.

	@var camera The camera object
	@var isCaptured Is this frame captured successfully?
	@var frame The frame captured from the web camera
	@var camera_thread The thread for capturing frames
	@var is_thread_started Is the camera_thread started?
	     It is also the flag for thread to keep running.
	@var read_lock The mutex for WebCamera.isCaptured and
	     WebCamera.frame
	"""

	def __init__(self, src = 0, width = 640, height = 480):
		"""Constuctor

		Create and set up the camera object. And initialize the instance
		attributes.

		@param src Specify the id of the web camera
		@param width Specify the width in pixel of the frame
		@param height Specify the height in pixel of the frame
		"""
		self.camera = cv2.VideoCapture(src)
		self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
		(self.isCaptured, self.frame) = self.camera.read()
		self.camera_thread = None
		self.is_thread_started = False
		self.read_lock = Lock()

	def __del__(self):
		"""Destructor

		Release the camera object.
		"""
		self.camera.release()

	def start_camera_thread(self):
		"""Start a new thread for capturing frames from the web camera

		The target method of the thread is WebCamera._camera_read_frame.
		If the camera thread is running, the method will output the
		message and do nothing.
		"""
		if self.is_thread_started:
			print("[INFO] The camera thread has been started.\n");
			return

		self.camera_thread = Thread(target = self._camera_read_frame)
		self.is_thread_started = True
		self.camera_thread.start()

	def stop_camera_thread(self):
		"""Stop the running thread

		If the camera thread haven't started yet, the method will do
		nothing.
		"""
		if self.camera_thread.is_alive():
			self.is_thread_started = False
			self.camera_thread.join()

	def _camera_read_frame(self):
		"""Keep capturing frames from the web camera

		The main job of the camera thread. The frame captured will be
		stored to WebCamera.frame, and WebCamera.isCaptured indicates
		that if this frame is captured successfully or not.

		Updating WebCamera.frame and WebCamera.isCaptured is in the
		critcal section.
		"""
		while self.is_thread_started:
			(isCaptured, frame) = self.camera.read()
			self.read_lock.acquire()
			(self.isCaptured, self.frame) = isCaptured, frame
			self.read_lock.release()

	def get_frame(self):
		"""Get the frame captured from the web camera

		@return The frame captured if the camera thread is running
		@return None if the camera thread is not running

		Getting frames read is in the critical section.
		"""
		if self.is_thread_started:
			self.read_lock.acquire()
			frame_read = self.frame.copy()
			self.read_lock.release()
			return frame_read
		else:
			return None
