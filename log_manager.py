import logging, time, os, queue
import logging.handlers

log_dir = "./log"

class ExecTimeFormatter(logging.Formatter):
	def format(self, record):
		relativeCreatedTime = int(record.relativeCreated)
		minute = int(relativeCreatedTime / 60000)
		relativeCreatedTime = relativeCreatedTime - minute * 60000
		second = int(relativeCreatedTime / 1000)
		millisecond = relativeCreatedTime - second * 1000
		record.execTime = "{0}:{1:02d}.{2:03d}".format(minute, second, millisecond)
		return super(ExecTimeFormatter, self).format(record)

def initialize_logger():
	if not os.path.exists(log_dir):
		os.mkdir(log_dir)

	timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

	file_handler = logging.handlers.RotatingFileHandler( \
		filename = "{0}/execution.log".format(log_dir), maxBytes = 2 * 1024 * 1024, \
		backupCount = 5)
	file_handler.setLevel(logging.DEBUG)
	file_log_formatter = ExecTimeFormatter( \
		fmt = "[%(execTime)10s] %(levelname)-8s %(threadName)-12s %(name)-27s %(message)s")
	file_handler.setFormatter(file_log_formatter)

	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	console_log_formatter = logging.Formatter( \
		fmt = "%(levelname)-8s %(name)-27s %(message)s")
	console_handler.setFormatter(console_log_formatter)

	que = queue.Queue()
	queue_handler = logging.handlers.QueueHandler(que)
	queue_handler.setLevel(logging.INFO)
	queue_listener = logging.handlers.QueueListener(que, console_handler)

	logger = logging.getLogger('')
	logger.setLevel(logging.DEBUG)
	logger.addHandler(file_handler)
	logger.addHandler(queue_handler)

	queue_listener.start()
	logger.debug("=== Start logging at {0} ===".format(timestamp))

	return logger, queue_listener

def end_logger():
	root_logger.debug("=== End logging ===\n")
	queue_listener.stop()
	logging.shutdown()

root_logger, queue_listener = initialize_logger()