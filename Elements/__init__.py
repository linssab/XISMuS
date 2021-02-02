import logging
logger = logging.getLogger("logfile")
logger.info("Booting Elements...")

logger.info("Importing Compounds...")
from .Compounds import *
logger.info("Importing EnergyLib...")
from .EnergyLib import *
logger.info("Elements ready!")
