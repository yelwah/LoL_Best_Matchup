from datetime import datetime, date
from os import path
import re

def needsUpdate(filepath: str):
    if not path.exists(filepath):
        return True
    else:
        epoch_time = path.getmtime(filepath)
        last_updated_date = datetime.fromtimestamp(epoch_time).date()
        todays_date = date.today()
        if last_updated_date != todays_date:
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


full_champ_pool = {
    "top": ["yone", "garen", "sion", "malphite"],
    "jungle": ["diana", "graves", "sejuani", "ekko", "vi"],
    "middle": ["diana", "ahri", "viktor", "fizz", "vel'koz"],
    "bottom": ["missfortune", "tristana", "jhin", "jinx", "ashe"],
    "support": ["braum", "thresh", "nautilus", "blitzcrank"],
}
# champ_pool: dict[str, list[str]]= {
#     "top":["yone", "akshan"],
#     "jungle": ["diana", "vi"],
#     "middle": ["viktor", "ahri", "yone", "akshan"],
#     "bottom": ["jhin", "samira"],
#     "support": ["thresh", "braum"],
# }
champ_pool: dict[str, list[str]]= {
    "top":["yone", "akshan"],
    "jungle": [],
    "middle": ["viktor", "ahri", "yone", "akshan"],
    "bottom": [],
    "support": [],
}
