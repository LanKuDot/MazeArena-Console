"""The essential player information table
"""

class PlayerInfo:
	def __init__(self):
		self.ID = None
		self.IP = None
		self.team = None
		self.color_bgr = None

class PlayerInfoTable:
	def __init__(self, player_info_T = PlayerInfo):
		self._player_info_T = player_info_T
		self._player_info_table = {}

	def add_player_info(self, player_ip):
		new_player_info = self._player_info_T()
		new_player_info.IP = player_ip
		self._player_info_table[player_ip] = new_player_info

	def delete_player_info(self, player_ip):
		target_player_info = self.get_player_info_by_IP(player_ip)

		if target_player_info is not None:
			self._player_info_table.pop(player_ip)

	def get_player_info_by_IP(self, player_ip):
		return self._player_info_table.get(player_ip)

	def register_player_ID(self, player_ip, *args):
		"""Register player ID and tean

		args will be (ID, team).
		"""
		target_player_info = self.get_player_info_by_ip(player_ip)

		if target_player_info is not None:
			target_player_info.ID = args[0]
			target_player_info.team = args[1]