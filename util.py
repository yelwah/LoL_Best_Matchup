from datetime import datetime, date, timedelta
from global_logger import logger
from os import path
import re

def needsUpdate(filepath: str, num_days: int):
    if not path.exists(filepath):
        return True
    else:
        epoch_time = path.getmtime(filepath)
        last_updated_date = datetime.fromtimestamp(epoch_time).date()
        todays_date = date.today()
        logger.debug(str(todays_date + timedelta(days=-(num_days)))
            + " >=? " + str(last_updated_date) + " = " + str((todays_date + 
            timedelta(days=-(4.5))) > last_updated_date))
        if (todays_date + timedelta(days=-(num_days))) > last_updated_date:
            return True
        else:
            return False


def cleanString(string: str) -> str:
    alphabetical_regex = re.compile('[^a-z]')
    return alphabetical_regex.sub('', string.lower())

def getMatchupHTMLSavePath(role: str, champ: str):
    return (
        "C:\\dev\\repos\\Python\\Best_Matchup\\data\\"
        + role
        + "\\html\\"
        + champ
        + "_matchups.html"
    )


def getSynergyHTMLSavePath(role: str, champ: str):
    return (
        "C:\\dev\\repos\\Python\\Best_Matchup\\data\\"
        + role
        + "\\html\\"
        + champ
        + "_synergies.html"
    )


def getMatchupCSVPath(role: str, champ: str):
    return (
        "C:\\dev\\repos\\Python\\Best_Matchup\\data\\"
        + role
        + "\\matchups\\"
        + champ
        + ".csv"
    )


def getSynergyCSVPath(role: str, champ: str):
    return (
        "C:\\dev\\repos\\Python\\Best_Matchup\\data\\"
        + role
        + "\\synergies\\"
        + champ
        + ".csv"
    )
champ_pool: dict[str, list[str]]= {
    "top":["illaoi", "malphite", "yone", "akshan"],
    "jungle": [],
    "middle": ["ahri", "yone", "akshan", "lissandra",],
    "bottom": [],
    "support": [],
}
# expanded_champ_pool: dict[str, list[str]]= {
#     "top":["yone", "garen", "illaoi", "malphite", "akshan", "diana", "lissandra"],
#     "jungle": [],
#     "middle": ["orianna", "ahri", "yone", "akshan", "diana", "lissandra", "viktor"],
#     "bottom": [],
#     "support": [],
# }
# expanded_champ_pool: dict[str, list[str]]= {
#     "top":["yone", "illaoi", "malphite", "akshan", "lissandra", "diana", "jax"],
#     "jungle": ["kayn", "jax", "brand", "diana"],
#     "middle": ["orianna", "ahri", "yone", "akshan", "diana", "lissandra", "viktor"],
#     "bottom": [],
#     "support": [],
# }
# champ_pool = expanded_champ_pool