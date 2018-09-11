from threading import Thread
from time import sleep

class JobThread():
	def __init__(self, target, name = "", call_every_sec = 0.0):
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
		if self._thread.is_alive():
			print("[JobThread] {0} thread has been already started." \
				.format(self._thread.name))
		else:
			self._is_thread_started = True
			self._thread.start()
			print("[JobThread] {0} thread is started." \
				.format(self._thread.name))

	def stop(self):
		if self._thread.is_alive():
			self._is_thread_started = False
			self._thread.join()
			print("[JobThread] {0} thread is stopped." \
				.format(self._thread.name))
		else:
			print("[JobThread] {0} thread has not been started yet." \
				.format(self._thread.name))

	def _thread_loop(self):
		while self._is_thread_started:
			self._fn_target()

	def _thread_loop_every_sec(self, timestep):
		while self._is_thread_started:
			self._fn_target()
			sleep(timestep)