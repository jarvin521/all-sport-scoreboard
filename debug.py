#import data.scoreboard_config
import time
import sys

# log filenames (can be changed by callers if necessary)
ERROR_LOG_FILE = "errors.log"
INFO_LOG_FILE = "info.log"

# control whether debug messages print to stdout
debug_enabled = False

def set_debug_status(config):
	"""Enable or disable debug printing based on the provided config object."""
	global debug_enabled
	debug_enabled = config.debug


def _write_to_file(filename, text):
	"""Append a line of text to the given file."""
	try:
		with open(filename, "a", encoding="utf-8") as f:
			f.write(text + "\n")
	except Exception:
		# fallback to stdout if file write fails
		print("[logging failure] could not write to %s" % filename)


def __debugprint(text):
	"""Print to stdout (used for debug/console output)."""
	print(text)
	sys.stdout.flush()


def log(text):
	if debug_enabled:
		msg = "DEBUG ({}): {}".format(__timestamp(), text)
		__debugprint(msg)
		# debug messages are treated like info for file logging
		_write_to_file(INFO_LOG_FILE, msg)


def warning(text):
	msg = "WARNING ({}): {}".format(__timestamp(), text)
	__debugprint(msg)
	# warnings go to info log by default
	_write_to_file(INFO_LOG_FILE, msg)


def error(text):
	msg = "ERROR ({}): {}".format(__timestamp(), text)
	__debugprint(msg)
	_write_to_file(ERROR_LOG_FILE, msg)


def info(text):
	msg = "INFO ({}): {}".format(__timestamp(), text)
	__debugprint(msg)
	_write_to_file(INFO_LOG_FILE, msg)


def __timestamp():
	return time.strftime("%H:%M:%S", time.localtime())
