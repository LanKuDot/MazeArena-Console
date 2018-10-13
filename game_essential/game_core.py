"""The essential functions in the game.
"""

import communication_server as comm_server
from .player_info import BasicTeamInfo, TeamType
from maze_manager import MazeManager, MazePositionFinder
from util.function_delegate import FunctionDelegate
		
class BasicGameCore:
	"""The basic functions in the game

	It manages players and handles the communication between players or
	the request of their position.

	@var _teams The dictionary of TeamType-TeamInfo pair to manage two teams
	@var _teammates The dictionary of player_IP-TeamType to find the team the
	     player belongs to
	@var _maze_manager The MazeManager object
	@var _comm_server The communication_server module
	@var _handlers The dictionary of situation-handlers for the external widgets
	     or class to set the callback functions. See BasicGameCore._handler_init()
	@var _is_game_started Is the game started?
	"""

	def __init__(self, maze_manager: MazeManager, \
		team_info_T = BasicTeamInfo):
		"""Constructor

		Constructor will invoke _set_handler_to_server() to set the callback
		function on communication_server module, _team_init() to initialize
		the variables of BasicTeamInfo, and _handler_init() to create the
		event handler for the external objects to set their callback functions.

		@param maze_manager Specify the MazeManager object
		@param team_info_T Specify BasicTeamInfo or its derived class
		"""
		self._teams = {
			TeamType.A: team_info_T(),
			TeamType.B: team_info_T()
		}
		self._teammates = {}
		self._maze_manager = maze_manager
		self._comm_server = comm_server
		self._handlers = {}

		self._is_game_started = False

		self._set_handler_to_server()
		self._team_init()
		self._handler_init()

	@property
	def is_game_started(self):
		"""Is the game started?

		The getter of BasicGameCore._is_game_started.
		"""
		return self._is_game_started

	def _set_handler_to_server(self):
		"""Set the callback functions to the communication_server module

		* Set player_quit() when a player disconnects from the server
		* Set player_join() when the server receives the command "join" from player
		* Set player_position() when the server receives the command "position"
		  from player
		* Set player_send_msg() when the server received the command "send-to"
		"""
		self._comm_server.set_disconnection_handler(self.player_quit)
		self._comm_server.add_command_handler("join", self.player_join)
		self._comm_server.add_command_handler("position", self.player_position)
		self._comm_server.add_command_handler("send-to", self.player_send_msg)

	def _team_init(self):
		"""Initialize the variables in the BasicTeamInfo

		The method will set the team_type and MazePositionFinder to both BasicTeamInfo
		"""
		for team_type, team_info in self._teams.items():
			team_info.team_type = team_type
			team_info.maze_pos_finder = \
				self._maze_manager._get_finder_by_team_name(team_type.__str__())

	def _handler_init(self):
		"""Create the event handlers

		Register the callbacks: `BasicGameCore._handlers[event_name] += handler`
		There are two handlers:
		* "player-join": Invoked in player_join(). The handler should be
		  `handler(player_info: BasicPlayerInfo, team_type, TeamType)`.
		* "player-quit": Invoked in player_quit(). The handler should be
		  `handler(player_info: BasicPlayerInfo, team_type, TeamType)`.
		"""
		self._handlers["player-join"] = FunctionDelegate()
		self._handlers["player-quit"] = FunctionDelegate()

	def team_set_name(self, team_type: TeamType, team_name):
		"""Set the name of the team

		The callback function for the widget that could enter the team name.

		@param team_type Specify the TeamType
		@param team_name Specify the name of the team
		"""
		self._teams[team_type].team_name = team_name
		print("[GameCore] Set the name of team {0} to \"{1}\"." \
			.format(team_type, team_name))

	def team_get_type_by_name(self, team_name) -> TeamType:
		"""Get the type of the team by the team name

		@param team_name Specify the name of the team
		@return The TeamType of the team
		@exception ValueError If the specified team name is not found
		"""
		for team_info in self._teams.values():
			if team_info.team_name == team_name:
				return team_info.team_type

		try:
			raise ValueError
		except ValueError as err:
			err.extra_info = "\"{0}\" is not a team name.".format(team_name)
			raise

	def player_join(self, player_ip, *args):
		"""The callback function when a player sends join command

		The command is: "join <player ID> <team name>".
		The response is: "server join ok" if it's success.
		or "server join fail" if one of the situations is occured:
		1. The argument is not matched;
		2. The specified <team name> is not found.

		The method will try to find the player's team and create a new
		player info for that player in his team.
		The BasicGameCore._teammates will record the player's team and then
		invoke the handler:
		`BasicGameCore._handler["player_join"](player_info, team_type)`

		@param player_ip Specify the IP of the player
		@param args Specify a tuple (player ID, team name)
		"""
		try:
			player_ID = args[0]
			team_name = args[1]
			team_type = self.team_get_type_by_name(team_name)
		except IndexError:	# Invaild arguments
			self._comm_server.send_message(player_ip, "join fail")
			print("[GameCore] The arguments for join the game are invaild.")
		except ValueError:	# Invaild team name
			self._comm_server.send_message(player_ip, "join fail")
			print("[GameCore] Specified team name {0} is not found.".format(team_name))
		else:
			# Check if the player ID is used in the team
			player_info = self._teams[team_type].get_player_info_by_ID(player_ID)
			if player_info is not None:
				self._comm_server.send_message(player_ip, "join fail")
				print("[GameCore] Player \"{0}\" is already in the team." \
					.format(player_ID))
				return

			player_info = self._teams[team_type] \
				.add_player_info(player_ip, player_ID, team_name)

			self._teammates[player_ip] = team_type
			self._handlers["player-join"].invoke(player_info, team_type)

			self._comm_server.send_message(player_ip, "join ok")

			print("[GameCore] Player \"{0}\" from {1} joins the team \"{2}\"." \
				.format(player_info.ID, player_info.IP, player_info.team_name))

	def player_quit(self, player_ip):
		"""The callback function when a player disconnection from the server

		The information of that player will be removed. It will also be removed
		from BasicGameCore._teammates. Then, invoke the handler:
		`BasicGameCore._handler["player_quit"](player_info, team_type)`

		@param player_ip Specify the IP of the player
		"""
		try:
			team_type = self._teammates.pop(player_ip)
		except KeyError:
			print("[GameCore] Specified player is not found.")
			return
		else:
			player_info = self._teams[team_type].delete_player_info(player_ip)

			self._handlers["player-quit"].invoke(player_info, team_type)

			print("[GameCore] Player \"{0}\" from {1} quits the game." \
				.format(player_info.ID, player_info.IP))

	def player_send_msg(self, player_ip, *args):
		"""Send the message to the other player

		@param player_ip Specify the IP of the player who sends the message
		@param args Specify a tuple (to_ID, message_block_1, message_block_2, ...).
		"""
		try:
			to_ID = args[0]
			message = args[1:len(args)]
			team_type = self._teammates[player_ip]
		except IndexError:	# Invalid arguments
			self._comm_server.send_message(player_ip, "send-to fail")
		except KeyError:	# Invalid player team
			self._comm_server.send_message(player_ip, "send-to fail")
		else:
			from_ID = self._teams[team_type].get_player_info_by_IP(player_ip).ID
			to_info = self._teams[team_type].get_player_info_by_ID(to_ID)
			if to_info is not None:
				msg_str = ""
				for msg_block in message:
					msg_str += " " + msg_block
				self._comm_server.send_message(to_info.IP, "send-from {0}{1}" \
					.format(from_ID, msg_str))
				self._comm_server.send_message(player_ip, "send-to ok")
			else:
				self._comm_server.send_message(player_ip, "send-to fail")

	def player_set_color(self, player_ip, color_bgr):
		"""Set the LED color of the player

		The callback function for the widget that can specify the LED color of
		the player's maze car.

		@param player_ip Specify the IP of the player
		@param color_bgr Specify the LED color in BGR domain
		"""
		for team_info in self._teams.values():
			# If the player_ip is not in that table,
			# it will do nothing.
			team_info.set_player_color(player_ip, color_bgr)

	def player_position(self, player_ip):
		"""Response the request of the position from the player

		The request is "position".
		The response is "position <x> <y>"; or "position -1 -1", if the color
		of the player in not registered in the MazeManager.

		@param player_IP Specify the IP of the player
		"""
		team_type = self._teammates[player_ip]
		maze_pos_finder = self._teams[team_type].maze_pos_finder
		player_info = self._teams[team_type].get_player_info_by_IP(player_ip)

		pos = maze_pos_finder.get_pos_in_maze(player_info.color_bgr)

		if pos is not None:
			self._comm_server.send_message(player_ip, "position {0} {1}" \
				.format(*pos))
		else:
			self._comm_server.send_message(player_ip, "position -1 -1")

	def game_start(self):
		"""Start the game

		It will do nothing if the game is already started.
		The server will broadcast a "game-start" message.
		"""
		if self._is_game_started:
			return

		self._comm_server.broadcast_message("game-start")
		self._is_game_started = True

	def game_stop(self):
		"""Stop the game

		If will do nothing if the game is already stopped.
		The server will broadcast a "game-stop" message.
		"""
		if not self._is_game_started:
			return

		self._comm_server.broadcast_message("game-stop")
		self._is_game_started = False
