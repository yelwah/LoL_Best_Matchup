import re
from datetime import date, datetime, timedelta
from os import path

from .global_logger import logger

PROJECT_ROOT_DIR = path.dirname(path.abspath(__file__))


def needsUpdate(filepath: str, num_days: int) -> bool:
    if not path.exists(filepath):
        return True
    else:
        epoch_time = path.getmtime(filepath)
        last_updated_date = datetime.fromtimestamp(epoch_time).date()
        todays_date = date.today()
        logger.debug(
            str(todays_date + timedelta(days=-(num_days)))
            + " >=? "
            + str(last_updated_date)
            + " = "
            + str((todays_date + timedelta(days=-(4.5))) > last_updated_date)
        )
        if (todays_date + timedelta(days=-(num_days))) > last_updated_date:
            return True
        else:
            return False


def cleanString(string: str) -> str:
    alphabetical_regex = re.compile("[^a-z]")
    return alphabetical_regex.sub("", string.lower())


def getMatchupHTMLSavePath(role: str, champ: str) -> str:
    return PROJECT_ROOT_DIR + "\\" + role + "\\html\\" + champ + "_matchups.html"


def getSynergyHTMLSavePath(role: str, champ: str) -> str:
    return PROJECT_ROOT_DIR + "\\" + role + "\\html\\" + champ + "_synergies.html"


def getMatchupCSVPath(role: str, champ: str) -> str:
    return PROJECT_ROOT_DIR + "\\" + role + "\\matchups\\" + champ + ".csv"


def getSynergyCSVPath(role: str, champ: str) -> str:
    return PROJECT_ROOT_DIR + "\\" + role + "\\synergies\\" + champ + ".csv"
