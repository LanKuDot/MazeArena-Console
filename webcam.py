"""@package docstring
Capture frames from the web camera.
"""

from threading import Thread, Lock
import cv2
import logging

class WebCamera:
	"""Capture frames from the web camera.

	It will create a new thread to get frames from the web camera.
	The camera thread has to be started first by invoking
	WebCamera.start_camera_thread, and then accessing frames captured
	by invoking WebCamera.get_frame.

	Note that if you want to access WebCamera.isCaptured and
	WebCamera.frame from another thread, you have to check the
	WebCamera.read_lock first.

	@var _camera The camera object
	@var isCaptured Is this frame captured successfully?
	@var frame The frame captured from the web camera
	@var _camera_thread The thread for capturing frames
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
		self._logger = logging.getLogger(self.__class__.__name__)
		self._camera = cv2.VideoCapture(src)
		self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
		(self.isCaptured, self.frame) = self._camera.read()
		self._camera_thread = None
		self.is_thread_started = False
		self.read_lock = Lock()

		self._logger.debug("Camera object created. " \
			"Resolution: {0} x {1}.".format(width, height))

	def release_camera(self):
		"""Release the camera object.
		"""
		self._logger.debug("Camera object released.")
		self._camera.release()

	def start_camera_thread(self):
		"""Start a new thread for capturing frames from the web camera

		The target method of the thread is WebCamera._camera_read_frame.
		If the camera thread is running, the method will output the
		message and do nothing.
		"""
		if self.is_thread_started:
			self._logger.info("The camera thread has been started.\n");
			return

		self._logger.debug("The camera thread is starting.")

		self._camera_thread = Thread(target = self._camera_read_frame, \
			name = "WebCamera")
		self.is_thread_started = True
		self._camera_thread.start()

	def stop_camera_thread(self):
		"""Stop the running thread

		If the camera thread haven't started yet, the method will do
		nothing.
		"""
		if self._camera_thread.is_alive():
			self._logger.debug("The camera thread is stopping.")

			self.is_thread_started = False
			self._camera_thread.join()

	def _camera_read_frame(self):
		"""Keep capturing frames from the web camera

		The main job of the camera thread. The frame captured will be
		stored to WebCamera.frame, and WebCamera.isCaptured indicates
		that if this frame is captured successfully or not.

		Updating WebCamera.frame and WebCamera.isCaptured is in the
		critcal section.
		"""
		self._logger.debug("The camera thread is started.")

		while self.is_thread_started:
			(isCaptured, frame) = self._camera.read()
			self.read_lock.acquire()
			(self.isCaptured, self.frame) = isCaptured, frame
			self.read_lock.release()

		self._logger.debug("The camera thread is stopped.")


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
