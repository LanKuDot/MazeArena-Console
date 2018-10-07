"""The essential player information table
"""

class BasicPlayerInfo:
	def __init__(self):
		self.ID = None
		self.IP = None
		self.team_name = ""
		self.color_bgr = None

class BasicPlayerInfoTable:
	def __init__(self, player_info_T = BasicPlayerInfo):
		self._player_info_T = player_info_T
		self._table = {}

	def add_player_info(self, player_ip, *args) -> BasicPlayerInfo:
		new_player_info = self._player_info_T()
		new_player_info.IP = player_ip
		new_player_info.ID = args[0]
		new_player_info.team_name = args[1]
		self._table[player_ip] = new_player_info
		return new_player_info

	def delete_player_info(self, player_ip):
		target_player_info = self.get_player_info_by_IP(player_ip)

		if target_player_info is not None:
			self._table.pop(player_ip)

	def get_player_info_by_IP(self, player_ip) -> BasicPlayerInfo:
		return self._table.get(player_ip)

	def set_player_color(self, player_ip, color_bgr):
		"""Set the LED color of the player

		@param player_ip Specify the player IP
		@param color_bgr Specify the LED color in BGr domain
		"""
		target_info = self.get_player_info_by_IP(player_ip)

		if target_info is not None:
			target_info.color_bgr = color_bgr
