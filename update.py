import global_logger

global_logger.init()

import web_scraping
import parse_lolalytics
from util import champ_pool

web_scraping.fetchLolalytics(champ_pool, force=bool(0))
parse_lolalytics.parseLolalytics(champ_pool)
