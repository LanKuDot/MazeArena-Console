from threading import Thread
from time import sleep

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
	@var _is_thread_started A flag controling the thread execution
	@var _thread A Thread object to run the target method
	"""

	def __init__(self, target, name = "", call_every_sec = 0.0):
		"""Constructor

		@param target Specify the target method to be run
		@param name Specify the thread name for recognition
		@param call_every_sec Specify the time interval in seconds
		       for running the target method
		"""
		self._fn_target = target
		self._is_thread_started = False
		# If name is not specified, set name to the target func name
		if not name:
			name = target.__name__

		if call_every_sec <= 0.0:
			self._thread = Thread(target = self._thread_loop, name = name)
		else:
			self._thread = Thread( \
				target = lambda: self._thread_loop_every_sec(call_every_sec), \
				name = name)

	def start(self):
		"""Start the job thread

		If the thread has been already started, the method does nothing.
		"""
		if self._thread.is_alive():
			print("[JobThread] {0} thread has been already started." \
				.format(self._thread.name))
		else:
			self._is_thread_started = True
			self._thread.start()
			print("[JobThread] {0} thread is started." \
				.format(self._thread.name))

	def stop(self):
		"""Stop the job thread

		If the thread is not alive, the method does nothing.
		"""
		if self._thread.is_alive():
			self._is_thread_started = False
			self._thread.join()
			print("[JobThread] {0} thread is stopped." \
				.format(self._thread.name))
		else:
			print("[JobThread] {0} thread has not been started yet." \
				.format(self._thread.name))

	def _thread_loop(self):
		"""A while loop for Thread to execute the target method
		"""
		while self._is_thread_started:
			self._fn_target()

	def _thread_loop_every_sec(self, time_interval):
		"""A while loop for Thread to execute the target method every n sec

		@param time_interval Specify the time interval
		"""
		while self._is_thread_started:
			self._fn_target()
			sleep(time_interval)