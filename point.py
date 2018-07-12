class Point2D():
	"""A data structure of 2d point

	@var x The x coordinate of the point
	@var y The y coordinate of the point
	"""
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y

	def __eq__(self, other):
		if self.x == other.x and self.y == other.y:
			return True
		return False

	def __ne__(self, other):
		return not self.__eq__(self, other)

	def __str__(self):
		return "({0}, {1})".format(self.x, self.y)

	def __repr__(self):
		return "Point2D({0}, {1})".format(self.x, self.y)
