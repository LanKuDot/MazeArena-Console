import os.path
import xml.etree.ElementTree as ET
import logging
from point import Point2D

class ConfigManager:
	"""Manage the configuration. Configuration are managed in xml foramt.

	@var config_file_path The path of the configuration file.
	     Create a new one if it doesn't exist.
	@param maze_config A dictionary for storing the configuration of the maze.
	     - "corner_plane_upper": 4 Point2D in a list to store the corner points
	       of the upper plane in the camera coordinate
	     - "corner_plane_lower": Similar to "corner_plane_upper" but for
	       the lower plane
	     - "scale": A Point2D to store the scale of the maze
	     - "wall_height": A float to store the wall height of the maze
	@param server_config A dictinary for storing the configuration of the server.
	     - "ip": A string to store the IP of the server
		 - "port": A int to store the port of the server
	"""

	def __init__(self, config_file_path):
		"""Constructor and load the configuration file

		@param _config_file_path Specify the file path of the configuration file
		"""
		self._logger = logging.getLogger(self.__class__.__name__)

		self._config_file_path = config_file_path
		self.maze_config = {
			"corner_plane_upper": \
				[Point2D(-1, -1), Point2D(-1, -1), Point2D(-1, -1), Point2D(-1, -1)],
			"corner_plane_lower": \
				[Point2D(-1, -1), Point2D(-1, -1), Point2D(-1, -1), Point2D(-1, -1)],
			"scale": Point2D(-1, -1),
			"wall_height": -1
		}
		self.server_config = {
			"ip": "127.0.0.1",
			"port": 5000
		}

		self._load_config()

	def _load_config(self):
		"""Load the configruation

		If the specified file dosen't exist, it will invoke
		ConfigManager.save_config() to create and initialize the configuration,
		and save to the file.
		"""
		if not os.path.isfile(self._config_file_path):
			self._logger.debug("Config file not found. Create a new one.")
			self.save_config()
			return

		self._logger.debug("Loading config file {0}".format(self._config_file_path))

		config_tree = ET.parse(self._config_file_path)
		config_root = config_tree.getroot()

		# Maze configuration
		self.maze_config["corner_plane_upper"].clear()
		corner_upper = config_root.find("./maze/corner[@plane='upper']")
		for point in list(corner_upper):
			x = int(point.attrib["x"])
			y = int(point.attrib["y"])
			self.maze_config["corner_plane_upper"].append(Point2D(x, y))
		self.maze_config["corner_plane_lower"].clear()
		corner_lower = config_root.find("./maze/corner[@plane='lower']")
		for point in list(corner_lower):
			x = int(point.attrib["x"])
			y = int(point.attrib["y"])
			self.maze_config["corner_plane_lower"].append(Point2D(x, y))
		maze_scale = config_root.find("./maze/scale/Point2D")
		self.maze_config["scale"] = Point2D( \
			int(maze_scale.attrib["x"]), int(maze_scale.attrib["y"]))
		maze_wall_height = config_root.find("./maze/wall_height")
		self.maze_config["wall_height"] = float(maze_wall_height.text)

		# Server configuration
		server_ip = config_root.find("./server/ip")
		self.server_config["ip"] = server_ip.text
		server_port = config_root.find("./server/port")
		self.server_config["port"] = int(server_port.text)

		self._logger.debug("Config file is loaded.")

	def save_config(self):
		"""Save the configuration to the xml file
		"""
		from xml.dom import minidom

		config_root = ET.Element("config")

		# Configuration of the maze
		maze = ET.SubElement(config_root, "maze")
		corner_upper = ET.SubElement(maze, "corner", {"plane": "upper"})
		for i in range(4):
			ET.SubElement(corner_upper, "Point2D", \
				{"x": str(self.maze_config["corner_plane_upper"][i].x), \
				 "y": str(self.maze_config["corner_plane_upper"][i].y)})
		corner_lower = ET.SubElement(maze, "corner", {"plane": "lower"})
		for i in range(4):
			ET.SubElement(corner_lower, "Point2D", \
				{"x": str(self.maze_config["corner_plane_lower"][i].x), \
				 "y": str(self.maze_config["corner_plane_lower"][i].y)})
		maze_scale = ET.SubElement(maze, "scale")
		ET.SubElement(maze_scale, "Point2D", \
			{"x": str(self.maze_config["scale"].x), \
			 "y": str(self.maze_config["scale"].y)})
		maze_wall_height = ET.SubElement(maze, "wall_height")
		maze_wall_height.text = str(self.maze_config["wall_height"])

		# Configuration of the server
		server = ET.SubElement(config_root, "server")
		server_ip = ET.SubElement(server, "ip")
		server_ip.text = self.server_config["ip"]
		server_port = ET.SubElement(server, "port")
		server_port.text = str(self.server_config["port"])

		rough_string = ET.tostring(config_root, "utf-8")
		reparsed_string = minidom.parseString(rough_string).toprettyxml(indent = "  ")

		self._logger.debug("Saving config file to {0}".format(self._config_file_path))
		with open(self._config_file_path, 'w') as f:
			f.write(reparsed_string)
		self._logger.debug("Config file is saved.")
