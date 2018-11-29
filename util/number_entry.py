from tkinter import *

class NonNegativeFloatEntry(Entry):
	def __init__(self, master, **options):
		vcmd = master.register(self._validate_nonNegative_float)
		super().__init__(master, validate = 'key', \
			validatecommand = (vcmd, '%d', '%P', '%S'), **options)

	def _validate_nonNegative_float(self, action, text_if_allowed, text_edited):
		"""Check if the character to be inserted to the entry is valid.

		If the character inserted makes the new text to be non negative float,
		return True.

		@param action Insertion('1') or Deletion('0')
		@param text_if_allowed The text will be if the validation is passed
		@param text_edited The text to be inserted or deleted
		"""
		# For entry.insert(0, 'blabla')
		if len(text_edited) > 1:
			if len(text_if_allowed) == 0:
				return True
			try:
				if float(text_if_allowed) >= 0:
					return True
				else:
					return False
			except ValueError:
				return False

		if action == '1':	# insertion
			if text_edited in '0123456789.+':
				try:
					float(text_if_allowed)
					return True
				except ValueError:
					return False
			else:
				return False
		elif action == '0':	# deletion
			return True

class PositiveIntEntry(Entry):
	def __init__(self, master, **options):
		vcmd = master.register(self._validate_positive_int)
		super().__init__(master, validate = 'key', \
			validatecommand = (vcmd, '%d', '%P', '%S'), **options)

	def _validate_positive_int(self, action, text_if_allowed, text_edited):
		if len(text_edited) > 1:
			if len(text_if_allowed) == 0:
					return True
			try:
				if int(text_if_allowed) > 0:
					return True
				else:
					return False
			except ValueError:
				return False

		if action == '1': # insertion
			if text_edited in '0123456789' and \
				int(text_if_allowed) > 0:
				return True
			else:
				return False
		elif action == '0': # deletion
			return True