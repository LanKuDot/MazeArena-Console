"""@package docstring

The module of TCP server. Start a TCP server on the specified
IP and port by a new thread. It provides callback functions
for new connection, disconnection, or receving message from
the client.
"""
import socket, select
from threading import Thread
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

### Data structure ###

class ClientSock:
	def __init__(self, sock):
		self.sock = sock
		self.to_be_closed = False

def start_server(server_ip: str, server_port: int):
	"""Start the TCP server on server_ip: server_port.

	If the server is running, it will do nothing. Otherwise,
	initialize the _sockets and _clients and start the server thread.

	@param server_ip Specify the IPv4 of the TCP server
	@param server_port Specify the port of the TCP server
	"""
	global _server_thread, _server_running

	if _server_running:
		return

	_sockets.clear()
	_clients.clear()
	_server_thread = Thread( \
		target = lambda: _listen_to_client(server_ip, server_port))
	_server_running = True
	_server_thread.start()

	print("[TCP server] Start server on {0}:{1}" \
		.format(server_ip, server_port))

def stop_server():
	"""Stop the TCP server

	If the server is not running, it will do nothing.
	"""
	global _server_running

	if not _server_running:
		return

	_server_running = False
	_server_thread.join()

	print("[TCP server] Stop server")

def is_running() -> bool:
	"""Is server running?
	"""
	return _server_running

def get_current_connection_num():
	"""Get the number of connections in the TCP server

	@return A tuple of (num of connections, max connection)
	"""
	return (len(_clients), MAX_CONNECTION)

def _listen_to_client(server_ip: str, server_port: int):
	"""Waiting for new connection from clients

	The mainloop of the TCP server. If there has new pending,
	it will accept new connection, receive message, or close connection.

	@param server_ip Specify the IP of the server
	@param server_port Specify the port of the server
	"""
	_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	_server_socket.bind((server_ip, server_port))
	_server_socket.listen(MAX_CONNECTION)

	# Add server socket to the checking list
	_sockets.append(_server_socket)

	while _server_running:
		# Checking sockets if there are incoming message for reading
		checking_sockets = _sockets.copy()
		read_sockets, _, _ = select.select(checking_sockets, [], [], 0.1)

		for sock in read_sockets:
			if sock == _server_socket:
				_new_connection(*(_server_socket.accept()))	
			else:
				_recv_msg(sock)

		# Check if the socket needs to be closed
		_check_disconnection()

	_server_socket.close()

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

	print("[TCP server] New connection from {0}" \
		.format(sock_ip))

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

	on_new_connect.invoke(sock_ip)

def _disconnection(sock):
	"""Close the connection from client

	Remove the socket from _socket and _clients, and close that socket.
	Then, invoke on_disconnection.

	@param sock The socket to be closed
	"""
	sock_ip = sock.getpeername()[0]

	print("[TCP server] Disconnection from {0}" \
		.format(sock_ip))

	_sockets.remove(sock)
	_clients.pop(sock_ip)

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
		print("[TCP server] {0} is not connecting to server" \
			.format(sock_ip))
		return
	else:
		client_sock.to_be_closed = True

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
		print("[TCP sevrer] Expection occured when receving data: {0}" \
			.format(e))
		_disconnection(sock)
	else:
		if len(recv_data) > 0:
			print("[TCP server] Receive data from {0}: {1}" \
				.format(sock_ip, recv_data))
			on_recv_msg.invoke(sock_ip, recv_data)
		else:
			_disconnection(sock)

def send_msg(to_ip: str, msg: str):
	"""Send message to a cllient.

	@param to_ip Specify the IP of the client
	@param msg Specify the message
	"""
	to_socket = _clients[to_ip].sock
	to_socket.send(msg.encode())

def broadcast_msg(msg: str):
	"""Boardcast message to all the clients

	@param msg Specify the message
	"""
	for ip in _clients.keys():
		send_msg(ip, msg)
