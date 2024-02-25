import analysis
import global_logger
from util import champ_pool

global_logger.init()

# TODO MAKE THIS A CONFIG FILE!!
my_role = "middle"
bans = ["", "", ""]
enemy_team = {"top": "", "jungle": "", "middle": "", "bottom": "", "support": ""}
ally_team = {"top": "", "jungle": "", "middle": "", "bottom": "", "support": ""}

analysis.bestPick(my_role, bans, champ_pool, enemy_team, ally_team)
