from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
import os
if os.name == 'nt':  # 'nt' means Windows
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:  # Assume Linux
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from utils import args, led_matrix_options
from data.data import Data
import debug

SCRIPT_NAME = "All Sports Scoreboard"
SCRIPT_VERSION = "1.0.0"

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options = matrixOptions)

# Print some basic info on startup
debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height))

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config", args)
debug.set_debug_status(config)

data = Data(config)

MainRenderer(matrix, data).render()