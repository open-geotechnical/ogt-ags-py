
import os
import sys

HERE_PATH =  os.path.abspath( os.path.dirname( __file__))
# make sure ogtgui in syspath
if not HERE_PATH in sys.path:
    sys.path.insert(0, HERE_PATH)

PROJECT_ROOT_PATH = os.path.join(HERE_PATH, "..")
"""Root dir of this project"""

ICONS_PATH = os.path.join(PROJECT_ROOT_PATH, "static", "icons")


