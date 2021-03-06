from threading import Thread
from time import sleep
import logging

class JobThread():
	"""A class that helps toggling a thread

	JobThread toggles the thread running flag with function calls and
	wraps the while loop into a function for thread to run. Just passing
	the method that you wants to run in the thread without adding an
	additional while loop. The method passed is run in
	JobThread._thread_loop() or JobThread._thread_loop_every_sec(), and
	the class will create a Thread to run either two methods.

	You can make thread do the job every n seconds by setting a positive
	value to call_every_sec at the constructor.

	@var _fn_target The target method to be run in JobThread. Note that
	     it don't need to add an additional while loop in the target method.
	@var _thread The Thread object that runs the target method
	@var _is_thread_started A flag controling the thread execution
	@var _name The identification name of the thread
	@var _call_every_sec The calling period of the target method. JobThread
	     invokes sleep(_call_every_sec) in the loop.
	"""

	def __init__(self, target, name = "", call_every_sec = 0.0):
		"""Constructor

		@param target Specify the target method to be run
		@param name Specify the thread name for recognition
		@param call_every_sec Specify the time interval in seconds
		       for running the target method
		"""
		self._logger = logging.getLogger(self.__class__.__name__)

		self._fn_target = target
		self._thread = None
		self._is_thread_started = False
		# If name is not specified, set name to the target func name
		if not name:
			self._name = target.__name__
		else:
			self._name = name
		self._call_every_sec = call_every_sec

	@property
	def is_running(self):
		"""Is the job thread running?
		"""
		return self._is_thread_started

	def start(self):
		"""Start the job thread

		If the thread has been already started, the method does nothing.
		"""
		if self._thread is not None and self._is_thread_started:
			self._logger.error("{0} thread has been already started." \
				.format(self._name))
		else:
			self._is_thread_started = True

			if self._call_every_sec <= 0.0:
				self._thread = Thread(target = self._thread_loop, name = self._name)
			else:
				self._thread = Thread( \
				target = lambda: self._thread_loop_every_sec(self._call_every_sec), \
				name = self._name)

			self._logger.debug("{0} thread is starting.".format(self._name))
			self._thread.start()

	def stop(self):
		"""Stop the job thread

		If the thread is not alive, the method does nothing.
		"""
		if self._thread is not None and self._is_thread_started:
			self._logger.debug("{0} thread is stopping.".format(self._name))
			self._is_thread_started = False
			self._thread.join()
		else:
			self._logger.warning("{0} thread has not been started yet." \
				.format(self._name))

	def stop_without_wait(self):
		"""Stop the job thread without waiting it terminates

		If the thread is not alive, the method does nothing.
		"""
		if self._thread is not None and self._is_thread_started:
			self._logger.debug("{0} thread is stopping without wait." \
				.format(self._name))

			self._is_thread_started = False
		else:
			self._logger.warning("{0} thread has not been started yet." \
				.format(self._name))

	def _thread_loop(self):
		"""A while loop for Thread to execute the target method
		"""
		self._logger.debug("{0} thread is started.".format(self._name))

		while self._is_thread_started:
			self._fn_target()

		self._logger.debug("{0} thread is stopped.".format(self._name))

	def _thread_loop_every_sec(self, time_interval):
		"""A while loop for Thread to execute the target method every n sec

		@param time_interval Specify the time interval
		"""
		self._logger.debug("{0} thread is started. " \
			"Will be executed every {1:6f} seconds." \
			.format(self._name, time_interval))

		while self._is_thread_started:
			self._fn_target()
			sleep(time_interval)

		self._logger.debug("{0} thread is stopped.".format(self._name))
