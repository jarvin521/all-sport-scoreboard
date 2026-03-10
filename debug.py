#import data.scoreboard_config
import time
import sys

import os

# control whether debug messages print to stdout
debug_enabled = False

# if the system has `logger` available we can send error messages
# directly to the systemd journal.  the code below calls the external
# command rather than depending on the python-systemd package so that
# nothing extra needs to be installed.

import subprocess


def _send_to_journal(msg):
    try:
        subprocess.run(["logger", "-t", "scoreboard", "-p", "user.err", msg],
                       check=False)
    except Exception:
        # if `logger` is missing or fails, just ignore it
        pass

def set_debug_status(config):
	"""Enable or disable debug printing based on the provided config object."""
	global debug_enabled
	debug_enabled = config.debug




def __debugprint(text):
	"""Print to stdout (used for debug/console output)."""
	print(text)
	sys.stdout.flush()


def log(text):
    if debug_enabled:
        msg = "DEBUG ({}): {}".format(__timestamp(), text)
        __debugprint(msg)


def warning(text):
    msg = "WARNING ({}): {}".format(__timestamp(), text)
    __debugprint(msg)


def error(text):
    msg = "ERROR ({}): {}".format(__timestamp(), text)
    __debugprint(msg)
    _send_to_journal(msg)


def info(text):
    msg = "INFO ({}): {}".format(__timestamp(), text)
    __debugprint(msg)


def __timestamp():
	return time.strftime("%H:%M:%S", time.localtime())
