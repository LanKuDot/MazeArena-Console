import logging, time, os, queue
import logging.handlers

log_dir = "./log"

def clear_old_log_file(remain_file_num: int):
	log_files = []
	for file_name in os.listdir(log_dir):
		if file_name.endswith(".log"):
			log_files.append(log_dir + "/" + file_name)

	while len(log_files) > remain_file_num:
		os.remove(log_files[0])
		log_files.pop(0)

def initialize_logger():
	if not os.path.exists(log_dir):
		os.mkdir(log_dir)

	timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

	file_handler = logging.FileHandler( \
		filename = "{0}/{1}.log".format(log_dir, timestamp))
	file_handler.setLevel(logging.DEBUG)
	file_log_formatter = logging.Formatter( \
		fmt = "[%(asctime)s] %(levelname)-8s %(threadName)-12s %(name)-27s %(message)s", \
		datefmt = "%H:%M")
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
	root_logger.debug("=== End logging ===")
	queue_listener.stop()
	logging.shutdown()

clear_old_log_file(5)
root_logger, queue_listener = initialize_logger()