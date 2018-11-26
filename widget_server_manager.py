from tkinter import *
import communication_server as comm_server

class WidgetServerManager(LabelFrame):
	"""The widget for controling the communication_server
	"""

	def __init__(self, master, **options):
		"""Constructor

		Set up the layout and register WidgetServerManager._update_connection_num
		to communication_server for updating the connection number to the
		widget.

		@param master Specify the parent widget
		@param options Specify addtional options to be passed to LableFrame
		"""
		super().__init__(master, text = "伺服器", **options)
		self.pack()

		self._setup_layout()

		comm_server.set_new_connection_handler(self._update_connection_num)
		comm_server.set_disconnection_handler(self._update_connection_num)

	def destroy(self):
		"""Override function. Stop the server thread if it is running.

		This method will be called when the GUI is closed.
		"""
		super().destroy()
		if comm_server.is_running():
			comm_server.remove_disconnection_handler(self._update_connection_num)
			comm_server.stop_server()

	def _setup_layout(self):
		"""Set up the layout of WidgetServerManager

		It will be like:
		+-----------------------------------------------
		| [Start Server] IP: [192.168.x.x] Port: [5000]
		+-----------------------------------------------
		------------------+
		 Connections: 1/8 |
		------------------+
		"""
		btn_toggle_server = Button(self, \
			text = "啟動伺服器", command = self._toggle_server, \
			name = "btn_toggle_server")
		btn_toggle_server.pack(side = LEFT)

		label_IP = Label(self, text = "IP: ", anchor = W)
		label_IP.pack(side = LEFT)
		entry_IP = Entry(self, width = 15, name = "entry_IP")
		entry_IP.pack(side = LEFT)
		label_port = Label(self, text = "Port: ", anchor = W)
		label_port.pack(side = LEFT)
		entry_port = Entry(self, width = 5, name = "entry_port")
		entry_port.pack(side = LEFT)

		label_connections = Label(self, text = "連接數: -/-", \
			name = "label_connections")
		label_connections.pack(side = LEFT)

	def _toggle_server(self):
		"""Toggle the communication server

		The callback function of the button of toggling server.

		Start the communication server when the server is not started,
		and vice versa.
		"""
		if not comm_server.is_running():
			server_ip = self.children["entry_IP"].get()
			server_port = int(self.children["entry_port"].get())
			comm_server.start_server(server_ip, server_port)

			self.children["btn_toggle_server"].config(text = "關閉伺服器")
			self._update_connection_num("")
		else:
			comm_server.stop_server()
			self.children["btn_toggle_server"].config(text = "啟動伺服器")
			self.children["label_connections"].config(text = "連接數: -/-")

	def _update_connection_num(self, client_ip):
		"""Update the text of connection numbers

		The callback function for new connection or disconnection
		in commnunication server.

		@param client_ip The argument for the caller, this value will be discard.
		"""
		cur_conn, max_conn = comm_server.get_current_connection_num()
		self.children["label_connections"].config( \
			text = "連接數: {0}/{1}".format(cur_conn, max_conn))
