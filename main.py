import global_logger
global_logger.init()

import analysis
from util import champ_pool

my_role = "middle"
bans = ["","",""]
enemy_team = {
  "top":     "",
  "jungle":  "",
  "middle":  "",
  "bottom":  "",
  "support": ""
}
ally_team = {
  "top":     "",
  "jungle":  "",
  "middle":  "",
  "bottom":  "",
  "support": ""
}

"""
bans = ["","",""]
enemy_team = {
  "top":     "",
  "jungle":  "",
  "middle":  "",
  "bottom":  "",
  "support": ""
}
ally_team = {
  "top":     "",
  "jungle":  "",
  "middle":  "",
  "bottom":  "",
  "support": ""
}
"""
analysis.bestPick(my_role, bans, champ_pool, enemy_team, ally_team)
