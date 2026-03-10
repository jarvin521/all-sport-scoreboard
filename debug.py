#import data.scoreboard_config
import time
import sys

import os

# directory where log files will live (defaults to same folder as this module)
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

# ensure the directory exists
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    # if the directory can't be created, fall back to current working directory
    LOG_DIR = os.getcwd()

# log filenames (can be changed by callers if necessary)
ERROR_LOG_FILE = os.path.join(LOG_DIR, "errors.log")
INFO_LOG_FILE = os.path.join(LOG_DIR, "info.log")

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
    except Exception as e:
        # fallback to stdout if file write fails, include exception message
        print(f"[logging failure] could not write to {filename}: {e}")


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
