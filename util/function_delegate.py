class FunctionDelegate:
	"""Provide the function invoking list to simulate function delegate

	Create a delegate: `a_delegate = FunctionDelegate()`
	Add a function to the delegate: `a_delegate += foo`
	Remove a function from the delegate: `a_delegate -= foo`
	Invoke the delegate: `a_delegate.invoke(*args)`. Note that
	FunctionDelegate won't check if the input arguments are correct.

	@var _function The function invoking list
	"""

	def __init__(self):
		"""Constructor
		"""
		self._functions = []

	def __iadd__(self, new_function):
		"""The overloading function of operator "+="

		Add a new function to the function invoking list.

		@param new_function Specify the function to be added
		@exception ValueError If the new_function is already in the
		    function invoking list.
		"""
		try:
			self._functions.index(new_function)
		except ValueError:
			self._functions.append(new_function)
			return self
		else:
			raise ValueError("'{0}' is already in the invoking list." \
				.format(new_function.__name__))

	def __isub__(self, target_function):
		"""The overloading function of operator "-="

		Remove a function from the function invoking list. 

		@param target_function Specify the function to be removed
		@exception ValueError if the target_function is not in the
		    function invoking list.
		"""
		self._functions.remove(target_function)
		return self

	def invoke(self, *args):
		"""Invoke all the functions in the function invoking list

		The method won't check if args are valid for all functions in the
		function invkong list or not.

		@param args Specify the arguments to be passed to the functions
		"""
		for function in self._functions:
			function(*args)
