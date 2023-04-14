import logging

logger = logging.getLogger("")
'''
  -- LOGGING LEVELS -- 
     CRITICAL  : 50
     ERROR     : 40
     WARNING   : 30
     INFO      : 20
     DEBUG     : 10
     NOSET     :  0
'''
def init():
  # function_only_format = "%(funcName)s(): %(message)s"
  # standard_format = "%(levelname)s: %(filename)s:%(lineno)d: %(funcName)s(): %(message)s"
  # logging.basicConfig(format=standard_format)
  standard_format = "%(levelname)s: %(message)s"
  logging.basicConfig(format=standard_format)
  logger.setLevel(logging.INFO)
  logger.debug("Logging initialized on program start-up")