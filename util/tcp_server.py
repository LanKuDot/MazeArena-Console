"""@package docstring

The module of TCP server. Start a TCP server on the specified
IP and port by a new thread. It provides callback functions
for new connection, disconnection, or receving message from
the client.
"""
import socket, select, time, logging
from threading import Thread
from queue import Queue
from util.function_delegate import FunctionDelegate

### Callback functions ###
# Add callbacks by '+=' operator, such as `on_new_connect += foo`.
# For new connection. It should be foo(client_ip: str).
on_new_connect = FunctionDelegate()
# For disconnection. It should be foo(client_ip: str).
on_disconnect = FunctionDelegate()
# For receving message from client. It should be foo(client_ip: str, message: str)
on_recv_msg = FunctionDelegate()

### Module variables ###
# The server socket
_server_socket = None
# The thread for running server. It will be _listen_to_client().
_server_thread = None
# Is server running?
_server_running = False
# The max connections can exist at the same time.
MAX_CONNECTION = 8
# The buffer size for receving message at a time.
RECV_BUFF_SIZE = 512
# A list for storing sockets, including server and clients.
_sockets = []
# A dictionary(IP, socket) which mapping IP to the socket.
_clients = {}
# The time interval of the request from the client.
request_interval = 0.1 # seconds
# The queue for the sending message
_sending_queue = Queue()
# Logger
_logger = logging.getLogger(__name__)

### Data structure ###
class ClientSock:
	def __init__(self, sock):
		self.sock = sock
		self.to_be_closed = False
		self.timestamp = time.time()

def start_server(server_ip: str, server_port: int) -> bool:
	"""Start the TCP server on server_ip: server_port.

	If the server is running, it will do nothing. Otherwise,
	initialize the _sockets and _clients and start the server thread.

	@param server_ip Specify the IPv4 of the TCP server
	@param server_port Specify the port of the TCP server
	@return True if the server successfully started
	"""
	global _server_thread, _server_running

	if _server_running:
		return

	_logger.debug("TCP server thread is starting.")

	_sockets.clear()
	_clients.clear()
	
	_server_socket = _create_server_socket(server_ip, server_port)
	if _server_socket is None:
		return False

	_server_thread = Thread( \
		target = lambda: _listen_to_client(_server_socket), \
		name = "tcp_server")
	_server_running = True
	_server_thread.start()

	_logger.info("Server is started on {0}:{1}" \
		.format(server_ip, server_port))

	return True

def stop_server():
	"""Stop the TCP server

	If the server is not running, it will do nothing.
	"""
	global _server_running

	if not _server_running:
		return

	_logger.debug("TCP server thread is stopping.")

	_server_running = False
	_server_thread.join()

	# Close all the client sockets
	for target_client in _clients.values():
		target_client.to_be_closed = True
	_check_disconnection()

	_logger.info("Server is stopped.")

def is_running() -> bool:
	"""Is server running?
	"""
	return _server_running

def get_current_connection_num():
	"""Get the number of connections in the TCP server

	@return A tuple of (num of connections, max connection)
	"""
	return (len(_clients), MAX_CONNECTION)

def _create_server_socket(server_ip: str, server_port: int) -> socket.socket:
	"""Create a server socket from giving imformation

	@param server_ip Specify the IP of the server
	@param server_port Specify the port of the server
	@return A created server socket
	@retval None If an exception occurs while creating the server socket.
	"""
	try:
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((server_ip, server_port))
		server_socket.listen(MAX_CONNECTION)
	except Exception as e:
		_logger.error("Exception occured while creating server socket: " \
			+ str(e))
		return None
	else:
		return server_socket

def _listen_to_client(server_socket):
	"""Waiting for new connection from clients

	The mainloop of the TCP server. If there has new pending,
	it will accept new connection, receive message, or close connection.
	"""
	# Add server socket to the checking list
	_sockets.append(server_socket)

	_logger.debug("TCP server thread is started.")

	while _server_running:
		# Checking sockets if there are incoming message for reading
		checking_sockets = _sockets.copy()
		read_sockets, _, _ = select.select(checking_sockets, [], [], 0.1)

		for sock in read_sockets:
			if sock == server_socket:
				_new_connection(*(server_socket.accept()))	
			else:
				_recv_msg(sock)

		_consume_sending_queue()
		# Check if the socket needs to be closed
		_check_disconnection()

	server_socket.close()

	_logger.debug("TCP server thread is stopped.")

def _new_connection(new_sock, addr_info):
	"""Accepct new connection

	If the IP of the new connection is already in the _client,
	it will close the old connection first, and then accept the new
	connection.

	The socket and the IP of the new connection is added to _socket
	and _clients. And then invoke on_new_connect.

	@param new_sock The socket of the new client
	@param addr_info The information of the new_sock
	"""
	global _sockets, _clients

	sock_ip = new_sock.getpeername()[0]

	try:
		# Check if the incoming connection is already in the list
		client_sock = _clients[sock_ip]
	except KeyError:
		pass
	else:
		# If it's in the list, disconnection the old connection
		_disconnection(client_sock.sock)
	finally:
		# Accept new connection
		_sockets.append(new_sock)
		_clients[sock_ip] = ClientSock(new_sock)

		_logger.info("New connection from {0}. Current clients: {1}" \
			.format(sock_ip, len(_clients)))

	on_new_connect.invoke(sock_ip)

def _disconnection(sock):
	"""Close the connection from client

	Remove the socket from _socket and _clients, and close that socket.
	Then, invoke on_disconnection.

	@param sock The socket to be closed
	"""
	sock_ip = sock.getpeername()[0]

	_sockets.remove(sock)
	_clients.pop(sock_ip)

	_logger.info("Disconnection from {0}. Current clients: {1}" \
		.format(sock_ip, len(_clients)))

	sock.close()
	on_disconnect.invoke(sock_ip)

def force_disconnection(sock_ip):
	"""Forcely close the connection from the client asychronizedly

	The method will only raise the close flag of the client socket.
	The server thread will not close the client until it checks the flag.
	"""
	try:
		client_sock = _clients[sock_ip]
	except KeyError:
		_logger.error("{0} is not connecting to server. " \
			"Cannot forcely disconnect it.".format(sock_ip))
		return
	else:
		client_sock.to_be_closed = True
		_logger.info("Forcely disconnect {0}".format(sock_ip))

def _check_disconnection():
	sock_to_be_closed = []

	# Stack sockets that need to be closed
	for client_sock in _clients.values():
		if client_sock.to_be_closed:
			sock_to_be_closed.append(client_sock)

	for client_sock in sock_to_be_closed:
		_disconnection(client_sock.sock)

def _recv_msg(sock):
	"""Receving message from the client

	If the exception occured when receving message, the client socket
	will be closed forcedly. The exception will be printed to the console.

	The received message is passed by invoking on_recv_msg.

	@param sock The socket that sending the message
	"""
	sock_ip = sock.getpeername()[0]

	try:
		recv_data = sock.recv(RECV_BUFF_SIZE).decode('utf-8')
	except Exception as e:
		_logger.error("Exception occured while receving data from {0}: {1}" \
			.format(sock_ip, e))
		_disconnection(sock)
	else:
		if len(recv_data) > 0:
			# Check timestamp to see whether handle the message or not.
			target_client = _clients[sock_ip]

			if time.time() - target_client.timestamp > request_interval:
				#_logger.debug("Receive data from {0}: {1}" \
				#	.format(sock_ip, recv_data))
				target_client.timestamp = time.time()
				on_recv_msg.invoke(sock_ip, recv_data)
		else:
			_disconnection(sock)

def _consume_sending_queue():
	while not _sending_queue.empty():
		message_item = _sending_queue.get()

		try:
			to_ip = message_item[0]
			message = message_item[1] + "\n"
			client = _clients[to_ip]

			total_msg_sent = 0
			while total_msg_sent < len(message):
				msg_sent = client.sock.send(message[total_msg_sent:].encode())
				if msg_sent == 0:
					raise RuntimeError("Socket connetion broken")
				total_msg_sent = total_msg_sent + msg_sent
			#_logger.debug("Send data to {0}: {1}".format(to_ip, message))
		except KeyError:
			_logger.error("Exception occured while sending data to {0}: "\
				"Client not found".format(to_ip))
		except Exception as e:
			_logger.error("Exception occured while sending data to {0}: {1}"\
				.format(to_ip, e))
			client.to_be_closed = True

def send_message(to_ip: str, msg: str):
	"""Send message to a cllient.

	The message item (to_ip, msg) will be pushed to the queue, and
	then consumed in _consume_sending_queue().

	@param to_ip Specify the IP of the client
	@param msg Specify the message
	"""
	_sending_queue.put((to_ip, msg))

def broadcast_message(msg: str):
	"""Boardcast message to all the clients

	@param msg Specify the message
	"""
	for ip in _clients.keys():
		send_message(ip, msg)
