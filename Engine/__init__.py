import logging
from .SpecRead import __PERSONAL__, __BIN__
logger = logging.getLogger("logfile")
logger.info("Booting Engine...")

logger.info("Importing Advcanced Fit...")
from .AdvFit import *
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
logger.info("Importing CBooster...")
try: from .CBooster import *
except OSError as e: 
    print(e)
    sys.exit(1)
logger.info("Engine modules ready!")

