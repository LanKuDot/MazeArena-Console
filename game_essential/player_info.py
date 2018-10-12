"""The essential player information table
"""
from enum import Enum, auto

class BasicPlayerInfo:
	"""A data struture for the player information

	@var ID The alias name of the player
	@var IP The IP of the player. It is the main searching key for the player.
	@var team_name The name of the team that this player belongs to
	@vat color_bgr The LED color of the player's maze car
	"""
	def __init__(self):
		self.ID = None
		self.IP = None
		self.team_name = ""
		self.color_bgr = None

class TeamType(Enum):
	"""A enum for the type of the team used to distinguish the different team

	@var A The team A. A.__str__() is "A".
	@var B The team B. B.__str__() is "B".
	"""
	A = auto()
	B = auto()

	def __str__(self):
		return {
			self.A: "A",
			self.B: "B"
		}.get(self)

class BasicTeamInfo:
	"""A data structure for managing the players in the same team

	The object of BasicPlayerInfo or its derived class will be created in the
	BasicTeamInfo.

	@var _player_info_T The BasicPlayerInfo or its derived class
	@var team_type The TeamType of the team
	@var maze_pos_finder The MazePositionFinder belongs to this team
	@var _players The dictionary stores the player IP-BasicPlayerInfo pair
	"""

	def __init__(self, player_info_T = BasicPlayerInfo):
		"""Constructor

		@param player_info_T Specify BasicPlayerInfo or its derived class
		"""
		self._player_info_T = player_info_T
		self.team_type = None
		self.team_name = ""
		self.maze_pos_finder = None
		self._players = {}

	def add_player_info(self, player_ip, player_ID, team_name) -> BasicPlayerInfo:
		"""Add the new player to this team

		The method will create a new player information and store to
		BasicTeamInfo._players.

		@param player_ip Specify the IP of the player
		@param player_ID Specify the ID of the player
		@param team_name Specify the name of the team this player belongs to
		@return The created player infomation object
		"""
		new_player_info = self._player_info_T()
		new_player_info.IP = player_ip
		new_player_info.ID = player_ID
		new_player_info.team_name = team_name
		self._players[player_ip] = new_player_info
		return new_player_info

	def delete_player_info(self, player_ip) -> BasicPlayerInfo:
		"""Delete a player from the team

		The specified player information will be removed from BasicTeamInfo._players.

		@param player_ip Specify the IP of the player
		@return The player information of the deleted player
		"""
		target_player_info = self.get_player_info_by_IP(player_ip)

		if target_player_info is not None:
			return self._players.pop(player_ip, None)

	def get_player_info_by_IP(self, player_ip) -> BasicPlayerInfo:
		"""Get the player infromation of the specified IP

		@param player_IP Specify the IP of the player
		@return The specified player information
		@retval None If it is not found
		"""
		return self._players.get(player_ip)

	def get_player_info_by_ID(self, player_ID) -> BasicPlayerInfo:
		"""Get the player information of the specified player ID

		@param player_ID Specify the ID of the player
		@return The specified player information
		@retval None If it is not found
		"""
		for player_info in self._players.values():
			if player_info.ID == player_ID:
				return player_info
		return None

	def set_player_color(self, player_ip, color_bgr):
		"""Set the LED color of the player

		@param player_ip Specify the player IP
		@param color_bgr Specify the LED color in BGR domain
		"""
		target_info = self.get_player_info_by_IP(player_ip)

		if target_info is not None:
			target_info.color_bgr = color_bgr
