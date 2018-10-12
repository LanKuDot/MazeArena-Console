"""@package docstring

The wrapper module of tcp_module. Mainly handling the command
send from the client.
"""
import util.tcp_server as TCPServer

# A dictionary for mapping command to the handler
_command_handlers = {}	# (command, handler)

def set_new_connection_handler(handler):
	"""Set the callback function(client_ip) of new connection from client
	"""
	TCPServer.on_new_connect += handler

def set_disconnection_handler(handler):
	"""Set the callback function(client_ip) of disconnection of client
	"""
	TCPServer.on_disconnect += handler

def add_command_handler(cmd_keyword: str, handler):
	"""Set the callback fucntion(from_ip, *args) of receving commands from client

	The arguments of the handle are (from_ip, *args_of_command).
	The command received from the client will be passed to _parse_command()
	to decide which handler function to be invoked. The command must be
	in the form of "<cmd> [param1] [param2] ...". _parse_command() will invoke
	the target handler by handler(from_ip, (para1, para2, ...)).

	@param cmd_keyword Specify the command
	@param handler Specify the callback function for that command
	@sa _parse_command
	"""
	try:
		_ = _command_handlers[cmd_keyword]
	except KeyError:
		_command_handlers[cmd_keyword] = handler
	else:
		raise ValueError("Command '{0}' is already registered." \
			.format(cmd_keyword))

def _parse_command(from_ip: str, cmd_string: str):
	"""Parse the command sent from the client

	This method is the callback function of tcp_server.on_recv_msg.

	The parameters of cmd_string should be seperated by whitespace,
	which is in the form of '<cmd> [param1] [param2]...'.
	The corresponding handler is invoked if the command string is
	registered by add_command_handler(). The parsed parameters is
	packed into a tuple and passed to the handler as the second
	parameter (The first one is client IP).

	If the received command is not registered, it will be discard.

	@param from_ip The IP of the client
	@param cmd_string The command recevied from the client
	"""
	spilted_str = cmd_string.split(' ')
	command = spilted_str[0]
	parameters = tuple(spilted_str[1:len(spilted_str)])

	try:
		target_handler = _command_handlers[command]
	except KeyError:
		print("[Communication server] Unknown command {0}. Discard." \
			.format(command))
	else:
		target_handler(from_ip, *parameters)

TCPServer.on_recv_msg += _parse_command

def toggle_server(server_ip: str, server_port: int):
	"""Toggle the TCP server

	@param server_ip Specify the IP of the server
	@param server_port Specify the port of the server
	"""
	if TCPServer.is_running():
		TCPServer.stop_server()
	else:
		TCPServer.start_server(server_ip, server_port)

# TODO: Is class better than the module?
def is_running():
	return TCPServer.is_running()

def get_current_connection_num():
	return TCPServer.get_current_connection_num()

def send_message(to_ip: str, msg: str):
	TCPServer.send_msg(to_ip, msg)

def broadcast_message(msg: str):
	TCPServer.broadcast_msg(msg)
