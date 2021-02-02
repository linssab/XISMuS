import logging
from .SpecRead import __PERSONAL__, __BIN__
logger = logging.getLogger("logfile")
logger.info("Booting Engine...")

logger.info("Importing SpecMath...")
from .SpecMath import *
logger.info("Importing SpecRead...")
from .SpecRead import *
logger.info("Importing ImgMath...")
from .ImgMath import *
logger.info("Importing Mapping...")
from .Mapping import *
logger.info("Importing MappingParallel...")
from .MappingParallel import *
logger.info("Importing BatchFitter...")
from .BatchFitter import *
logger.info("Engine modules ready!")

