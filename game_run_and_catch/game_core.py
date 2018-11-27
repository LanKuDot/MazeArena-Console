"""The game core of the game "Run and Catch"
"""

from game_essential import BasicGameCore
from game_essential import BasicPlayerInfo, BasicTeamInfo, TeamType
from maze_manager import MazeManager, MazePosition
from point import Point2D
from util.job_thread import JobThread
from util.function_delegate import FunctionDelegate

class PlayerInfo(BasicPlayerInfo):
	def __init__(self):
		super().__init__()
		self.is_catched = False

class TeamInfo(BasicTeamInfo):
	def __init__(self):
		super().__init__(PlayerInfo)

class GameCore(BasicGameCore):
	"""The game core of the game

	Team A is Team Catcher. Team B is the Team Runner.
	"""
	# The alias of the TeamType
	TEAM_CATCHER = TeamType.A
	TEAM_RUNNER = TeamType.B
	# The alias of the connection bit
	SIDE_UP = 1 << 0
	SIDE_RIGHT = 1 << 1
	SIDE_DOWN = 1 << 2
	SIDE_LEFT = 1 << 3

	def __init__(self, maze_manager: MazeManager):
		super().__init__(maze_manager, TeamInfo)

		self._num_of_survivor = 0
		self._maze_map = None
		self._init_maze_map()

		self.gamecore_thread = JobThread(self.gamecore, call_every_sec = 0.01)

	def _init_maze_map(self):
		"""Initialize the connections between each block in the maze

		Each block has 4 bits to record the connections to the 4 nearby blocks.
		The 4 bits repesent 4 directions, which are UP (bit 0), RIGHT (bit 1),
		DOWN (bit 2), and LEFT (bit 3).
		If there is no wall between two blocks, then the bit is set.
		"""
		# Create a 8 x 8 2D list
		self._maze_map = [[0 for col in range(8)] for row in range(8)]

		with open("game_run_and_catch/maze_map.txt") as f:
			for row in range(len(self._maze_map)):
				for col in range(len(self._maze_map[row])):
					data = ""
					# Ignore newline or the line started with '#'
					while len(data) <= 1 or data[0] == '#':
						data = f.readline()

					# Map data is a binary number
					self._maze_map[row][col] = int(data, 2)

	def _set_handler_to_server(self):
		super()._set_handler_to_server()
		self._comm_server.add_command_handler("game-touch", self.game_touch)
		self._comm_server.add_command_handler("position-team", self.player_position_team)
		self._comm_server.add_command_handler("position-enemy", self.player_position_enemy)

	def _handler_init(self):
		super()._handler_init()
		self._handlers["game-catched"] = FunctionDelegate()

	# @BasicGameCore.game_started
	def player_position_team(self, player_ip):
		"""Request the position of maze cars in the player's team (including itself)

		The request is `"position-team"`.
		The reply is `"position-team" [<player-id> <x> <y>]+`.

		Note that if the request is sent from the player who is catched, it won't
		reply the request.
		"""
		reply_msg = "position-team"

		team_type = self._teammates[player_ip]
		player_info = self._teams[team_type].get_player_info_by_IP(player_ip)

		if player_info.is_catched:
			return

		maze_pos_finder = self._teams[team_type].maze_pos_finder

		for player_info in self._teams[team_type]._players.values():
			reply_msg += " " + player_info.ID

			pos = maze_pos_finder.get_maze_pos(player_info.color_bgr)
			if pos is not None:
				reply_msg += " {0} {1}".format(*pos.position)
			else:
				reply_msg += " -1 -1"

		self._comm_server.send_message(player_ip, reply_msg)

	# @BasicGameCore.game_started
	def player_position_enemy(self, player_ip):
		"""Request the position of enemies

		The request is `"position-enemy"`.
		The reply is `"position-enemy" [<x> <y>]+`

		Note that if the request is sent from the player who is catched, it won't
		reply the request.
		"""
		reply_msg = "position-enemy"

		team_type = self._teammates[player_ip]
		player_info = self._teams[team_type].get_player_info_by_IP(player_ip)

		if player_info.is_catched:
			return

		if team_type is GameCore.TEAM_RUNNER:
			target_team_type = GameCore.TEAM_CATCHER
		else:
			target_team_type = GameCore.TEAM_RUNNER

		maze_pos_finder = self._teams[target_team_type].maze_pos_finder

		for player_info in self._teams[target_team_type]._players.values():
			pos = maze_pos_finder.get_maze_pos(player_info.color_bgr)
			if pos is not None:
				reply_msg += " {0} {1}".format(*pos.position)
			else:
				reply_msg += " -1 -1"

		self._comm_server.send_message(player_ip, reply_msg)

	@BasicGameCore.game_started
	def game_touch(self, player_ip):
		"""Touch the goal.

		Only the command sent from the runner side is valid.
		"""
		player_info = self._teams[GameCore.TEAM_RUNNER].get_player_info_by_IP(player_ip)
		if player_info is not None:
			self.game_stop()

	@BasicGameCore.game_stopped
	def game_start(self):
		self._num_of_survivor = self._teams[GameCore.TEAM_RUNNER].num_of_players()
		for player_info in self._teams[GameCore.TEAM_RUNNER]._players.values():
			player_info.is_catched = False
		self.gamecore_thread.start()
		super().game_start()

	@BasicGameCore.game_started
	def game_stop(self):
		self.gamecore_thread.stop_without_wait()
		super().game_stop()

	def gamecore(self):
		"""Keep tracking the status of the runners and the catchers

		The method will get the maze position of all the players, and
		test each runner-catcher pair. If the runner is catched by a catcher,
		the method will send a "game-catched" to the runner, and set the status
		of that runner to "catched". Then, invoke the handler of "game-catched".

		If there is no runner who is still alive, then the game will be stopped.
		"""
		runners = self._teams[GameCore.TEAM_RUNNER].maze_pos_finder.get_all_maze_pos()
		catchers = self._teams[GameCore.TEAM_CATCHER].maze_pos_finder.get_all_maze_pos()

		for runner in runners:
			for catcher in catchers:
				if self.is_catch(runner, catcher):
					runner_info = self._teams[GameCore.TEAM_RUNNER] \
						.get_player_info_by_color(runner.color_bgr)
					catcher_info = self._teams[GameCore.TEAM_CATCHER] \
						.get_player_info_by_color(catcher.color_bgr)
					if runner_info is None or catcher_info is None or \
						runner_info.is_catched:
						continue

					runner_info.is_catched = True
					self._comm_server.send_message(runner_info.IP, "game-catched")
					self._handlers["game-catched"].invoke(runner_info.IP)
					self._num_of_survivor -= 1

					print("[GameCore] Runner \"{0}\" is catched by \"{1}\"." \
						.format(runner_info.ID, catcher_info.ID))
					break

		if self._num_of_survivor <= 0:
			self.game_stop()

	def is_catch(self, runner: MazePosition, catcher: MazePosition) -> bool:
		"""Check if the catcher catches the runner
		"""
		# Neither runner nor catcher is in the maze, return False.
		if runner.position_detail.x < 0 or catcher.position_detail.x < 0:
			return False

		if Point2D.distance(runner.position_detail, catcher.position_detail) < 12.0:
			if catcher.position == runner.position:
				return True

			# Use the position of the runner as the reference point
			connection_bit = {
				Point2D(0, 1): GameCore.SIDE_UP,
				Point2D(1, 0): GameCore.SIDE_RIGHT,
				Point2D(0, -1): GameCore.SIDE_DOWN,
				Point2D(-1, 0): GameCore.SIDE_LEFT
			}.get(catcher.position - runner.position, 0)

			# If the block where the runner at and the block where the cather at
			# is connected, return True
			if self._maze_map[runner.position.y][runner.position.x] & connection_bit != 0:
				return True

		return False
