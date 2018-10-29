from collections import namedtuple
import math

class Point2D(namedtuple('Point2D', 'x y')):
	"""A data structure of 2d point

	@var x The x coordinate of the point
	@var y The y coordinate of the point
	"""
	__slots__ = ()

	def __str__(self):
		return "({0}, {1})".format(self.x, self.y)

	def __repr__(self):
		return "Point2D({0}, {1})".format(self.x, self.y)

	def __add__(self, other):
		return Point2D(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return Point2D(self.x - other.x, self.y - other.y)

	@staticmethod
	def distance(a, b):
		return math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
