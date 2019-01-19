"""@package docstring

The wrapper module of tcp_module. Mainly handling the command
send from the client.
"""
import util.tcp_server as TCPServer
import logging
from threading import Thread
from queue import Queue

# A dictionary for mapping command to the handler
_command_handlers = {}	# (command, handler)
# The thread for handling the pending command
_command_thread = None
# A queue to store the pending command
_pending_queue = Queue()
# Logger
_logger = logging.getLogger(__name__)

def set_new_connection_handler(handler):
	"""Set the callback function(client_ip) when a client connects to the server
	"""
	TCPServer.on_new_connect += handler

def remove_new_connection_handler(handler):
	"""Remove the callback function when a client connects to the server
	"""
	TCPServer.on_new_connect -= handler

def set_disconnection_handler(handler):
	"""Set the callback function(client_ip) when a client disconnects from the server
	"""
	TCPServer.on_disconnect += handler

def remove_disconnection_handler(handler):
	"""Remove the callback function when a client disconnects from the server
	"""
	TCPServer.on_disconnect -= handler

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

def _comsume_command():
	"""Comsume the pending commands in the _pending_queue

	This method is the target method of the thread _command_thread.
	The thread will stop when get the None object from the _pending_queue.
	"""
	_logger.debug("Consuming command thread is started.")

	while True:
		command_item = _pending_queue.get()

		if command_item is None:
			_pending_queue.task_done()
			break

		_parse_command(*command_item)
		_pending_queue.task_done()

	_logger.debug("Consuming command thread is stopped.")

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
		_logger.error("Unknown command {0} from {1}. Discard." \
			.format(command, from_ip))
	else:
		target_handler(from_ip, *parameters)

def _queue_command(from_ip: str, cmd_string: str):
	"""Queue the pending command to the _pending_queue

	The command in the _pending_queue will be comsumed in _dequeue_command.

	@param from_ip The IP of the client
	@param cmd_string The command recevied from the client
	"""
	_pending_queue.put((from_ip, cmd_string))

TCPServer.on_recv_msg += _queue_command

# TODO: Is class better than the module?
def start_server(server_ip: str, server_port: int) -> bool:
	"""Start the TCP server and the command thread

	@param server_ip Specify the IP of the server
	@param server_port Specify the port of the server
	@return True If the server successfully started.
	"""
	global _command_thread

	if not TCPServer.start_server(server_ip, server_port):
		return False

	_logger.debug("Consuming command thread is starting.")
	_command_thread = Thread(target = _comsume_command, name = "consume_cmd")
	_command_thread.start()

	return True

def stop_server():
	"""Stop the TCP server and the command thread
	"""
	_logger.debug("Consuming command thread is stopping.")
	_pending_queue.put(None)
	_pending_queue.join()
	_command_thread.join()
	TCPServer.stop_server()

def force_disconnection(client_ip):
	"""Forcely disconnect the client from the server

	@param client_ip Specify the client IP
	"""
	TCPServer.force_disconnection(client_ip)

def is_running():
	return TCPServer.is_running()

def get_current_connection_num():
	return TCPServer.get_current_connection_num()

def send_message(to_ip: str, msg: str):
	TCPServer.send_message(to_ip, msg)

def broadcast_message(msg: str):
	TCPServer.broadcast_message(msg)
