"""The widget of timer
"""

import time
import tkinter.font as font
from tkinter import *

from util.job_thread import JobThread

class TimerWidget(Frame):
	"""A widget of countdown timer

	@var _fn_on_times_up The callback function when time is up.
	     Invoked in _times_up().
	@var _timer_thread A JobThread for countdown. The target method
	     is _timer().
	@var _label_minute The Label widget for showing minute
	@var _label_second The Label widget for showing second
	@var _label_ms The Label widget for showing millisecond
	@var _is_countdown A variable to trace whether needs to countdown or not
	@var _time_left_in_ms The time left in milliseconds
	@var _time_at_last_update The time stamp of the last update the valie
	     _time_left_in_ms
	"""

	def __init__(self, master, fn_on_times_up, **options):
		"""Constructor

		@param fn_on_times_up Specify the callback function when time is up
		@param options Specify other options for the Frame widget
		"""
		super().__init__(master, **options)
		self.pack()

		self._fn_on_times_up = fn_on_times_up
		self._timer_thread = JobThread(self._timer, "timer", 0.02)
		self._fn_time_update = None

		self._label_minute = None
		self._label_second = None
		self._label_ms = None
		self._is_countdown = IntVar(self)
		self._is_countdown.trace("w", self._toggle_entry)

		self._time_in_ms = 0
		self._time_at_last_update = 0

		self._setup_layout()

	def _setup_layout(self):
		"""Set up the layout

		It will be:
		+-------------------------+
		| 00:00.0 [ ] min [ ] sec |
		+-------------------------+
		"""
		font_L = font.Font(family = "Consolas", size = 20)

		self._label_minute = Label(self, text = "00", font = font_L)
		self._label_minute.pack(side = LEFT)
		colon = Label(self, text = ":", font = font_L)
		colon.pack(side = LEFT)
		self._label_second = Label(self, text = "00", font = font_L)
		self._label_second.pack(side = LEFT)
		self._label_ms = Label(self, text = ".0", font = font_L)
		self._label_ms.pack(side = LEFT, fill = Y)

		space_holder = Label(self, text = "", width = 1)
		space_holder.pack(side = LEFT)

		checkbox = Checkbutton(self, text = "倒數", variable = self._is_countdown)
		checkbox.pack(side = LEFT)

		entry_minute = Entry(self, width = 2, name = "entry_minute", state = DISABLED)
		entry_minute.insert(0, "0")
		entry_minute.pack(side = LEFT)
		label_m = Label(self, text = "分")
		label_m.pack(side = LEFT)
		entry_second = Entry(self, width = 2, name = "entry_second", state = DISABLED)
		entry_second.insert(0, "0")
		entry_second.pack(side = LEFT)
		label_s = Label(self, text = "秒")
		label_s.pack(side = LEFT)

	def _toggle_entry(self, *args):
		"""Toggle the entries of the timer value setting

		If the countdown checkbox is checked, active these entries;
		otherwise, inactive them.
		"""
		if self._is_countdown.get() == 0:
			self.children["entry_minute"].config(state = DISABLED)
			self.children["entry_second"].config(state = DISABLED)
		else:
			self.children["entry_minute"].config(state = NORMAL)
			self.children["entry_second"].config(state = NORMAL)

	def _set_timer(self):
		"""Get values set in the entry and initialize the timer

		If there are invaild values (i.e. string) in the entry,
		the timer will be set to 00:00.

		The minute will be clamped to the range [0, 99], and
		the second will be clamped to the range [0, 59]
		"""
		try:
			minute_value = int(self.children["entry_minute"].get())
			second_value = int(self.children["entry_second"].get())
		except ValueError:
			minute_value = second_value = 0
		else:
			minute_value = max(0, min(minute_value, 99))	# clamp(0, 99)
			second_value = max(0, min(second_value, 59))	# clamp(0, 59)
		finally:
			self._update_timer(minute_value, second_value, 0)
			self._time_in_ms = minute_value * 600 + second_value * 10

	def _reset_timer(self):
		"""Reset the timer to 0:00
		"""
		self._update_timer(0, 0, 0)
		self._time_in_ms = 0

	def _update_timer(self, minute, second, ms):
		"""Update the timer text
		"""
		self._label_minute.config(text = "{:02d}".format(minute))
		self._label_second.config(text = "{:02d}".format(second))
		self._label_ms.config(text = ".{0}".format(ms))

	def timer_start(self):
		"""Initialize and start the timer

		If the timer has been already started, it will do nothing.
		"""
		if self._timer_thread.is_running:
			return

		if self._is_countdown.get() == 0:
			self._reset_timer()
			self._fn_time_update = self._count_up
		else:
			self._set_timer()
			self._fn_time_update = self._count_down

		self._time_at_last_update = time.time()
		self._timer_thread.start()

	def timer_stop(self):
		"""Stop the timer

		If the timer has been already stopped, it will do nothing.
		"""
		self._timer_thread.stop()

	def _times_up(self):
		"""Invoked when the time is up

		The method will invoke _fn_on_times_up().
		"""
		self._timer_thread.stop_without_wait()
		self._fn_on_times_up()

	def _timer(self):
		"""Update the timer every 0.1 seconds

		The target function of the _timer_thread.
		"""
		if time.time() - self._time_at_last_update > 0.1:
			self._time_at_last_update = time.time()
			self._fn_time_update()

	def _count_down(self):
		"""Countdown the timer every 0.1 seconds
		"""
		self._time_in_ms -= 1
		minute_value = int(self._time_in_ms / 600)
		second_value = int(self._time_in_ms / 10) - minute_value * 60
		ms_value = self._time_in_ms % 10
		self._update_timer(minute_value, second_value, ms_value)

		if self._time_in_ms <= 0:
			self._times_up()

	def _count_up(self):
		"""Countup the timer every 0.1 seconds
		"""
		self._time_in_ms += 1
		minute_value = int(self._time_in_ms / 600)
		second_value = int(self._time_in_ms / 10) - minute_value * 60
		ms_value = self._time_in_ms % 10
		self._update_timer(minute_value, second_value, ms_value)