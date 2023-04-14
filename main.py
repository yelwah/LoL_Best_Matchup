import global_logger
global_logger.init()

import analysis
from util import champ_pool

"""
  "top":     "",
  "jungle":  "",
  "middle":  "",
  "bottom":  "",
  "support": ""
"""
bans = ["", 
        "", 
        ""]
enemy_team = {
  "top":     "volibear",
  "jungle":  "maokai",
  "middle":  "vex",
  "bottom":  "",
  "support": "rakan"
}
ally_team = {
  "top":     "yone",
  "jungle":  "nidalee",
  "middle":  "",
  "bottom":  "",
  "support": "sona"
}
analysis.bestPick("middle", bans, champ_pool, enemy_team, ally_team)


