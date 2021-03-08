import logging
logger = logging.getLogger("logfile")
logger.info("Booting GUI...")

logger.info("Importing AdvCalibration...")
from .AdvCalibration import *
logger.info("Importing FitPanels...")
from .FitPanels import *
logger.info("Importing ProgressBar...")
from .ProgressBar import *
logger.info("Importing Theme...")
from .Theme import *
logger.info("GUI ready!")
