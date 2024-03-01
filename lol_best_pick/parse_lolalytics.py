import os
import re
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup, PageElement

from .global_logger import logger
from .util import (
    cleanString,
    getMatchupCSVPath,
    getMatchupHTMLSavePath,
    getSynergyCSVPath,
    getSynergyHTMLSavePath,
    needsUpdate,
)

ROLES = ["top", "jungle", "middle", "bottom", "support"]
stat_types = ["wr", "delta1", "delta2", "pr", "games"]


def parseLolalytics(pool: dict[str, list[str]], force: bool = False) -> None:
    print("\n Parsing newly updated matchup data from Lolalytics\n" + ("*" * 80))
    at_least_one_parsed = False
    for my_role, my_champs in pool.items():
        for champ in my_champs:
            # Fix up the string to be all lower no apostophes
            cleanString(champ)

            # If necessary, parse the matchup data for this champion in this role
            matchup_csv_path = getMatchupCSVPath(my_role, champ)
            matchup_html_path = getMatchupHTMLSavePath(my_role, champ)

            if os.path.exists(matchup_html_path) and (
                needsUpdate(matchup_csv_path, 1) or force
            ):
                at_least_one_parsed = True
                # Print which Champion is being Parsed
                logger.info("PARSING DATA FOR " + champ.upper() + " " + my_role.upper())

                # Load the Matchup HTML page from file
                with open(matchup_html_path, encoding="utf-8") as fp:
                    matchup_soup = BeautifulSoup(fp, "lxml")
                print(f"os.remove({matchup_html_path})")
                os.remove(matchup_html_path)
                matchups_df = getMatchupsDataFrame(matchup_soup)

                matchups_df.to_csv(matchup_csv_path)

            # If necessary, parse the synergy data for this champion in this role
            synergy_csv_path = getSynergyCSVPath(my_role, champ)
            synergy_html_path = getSynergyHTMLSavePath(my_role, champ)

            if os.path.exists(synergy_html_path) and (
                needsUpdate(synergy_csv_path, 1) or force
            ):
                at_least_one_parsed = True
                # Load the Synergy HTML page from file
                with open(synergy_html_path, encoding="utf-8") as fp:
                    synergy_soup = BeautifulSoup(fp, "lxml")
                print(f"os.remove({synergy_html_path})")
                os.remove(synergy_html_path)
                synergies_df = getSynergiesDataFrame(synergy_soup)

                synergies_df.to_csv(synergy_csv_path)
    if not at_least_one_parsed:
        print("All current matchups and synergies are already parsed.")
    print("\nParsing complete.\n")


def getMatchupsDataFrame(matchup_soup: BeautifulSoup) -> pd.DataFrame:
    matchups_df = pd.DataFrame(columns=(["id", "role", "champ"] + stat_types))
    matchups_df.set_index("id")

    for cur_proc_role in ROLES:
        print("Finding matchups for " + str(cur_proc_role))
        matchup_cells: list[PageElement] = matchup_soup.find_all(
            "div", {"class": "Cell_cell__383UV"}
        )
        cur_role_matchups: list[PageElement] = []
        for matchup in matchup_cells:
            regex = re.compile(r".+vslane=" + cur_proc_role)
            if matchup.find_next("a", href=regex) is not None:
                cur_role_matchups.append(matchup)
        parseMatchupsForRole(cur_proc_role, cur_role_matchups, matchups_df)

    return matchups_df


def getSynergiesDataFrame(synergy_soup: BeautifulSoup) -> pd.DataFrame:
    synergies_df = pd.DataFrame(columns=(["id", "role", "champ"] + stat_types))
    synergies_df.set_index("id")

    for cur_proc_role in ROLES:
        print("Finding synergies for " + str(cur_proc_role))
        synergy_cells = synergy_soup.find_all("div", {"class": "Cell_cell__383UV"})
        cur_role_synergy = []
        for synergy in synergy_cells:
            regex = re.compile(r".+lane=" + cur_proc_role)
            if synergy.find("a", href=regex) is not None:
                cur_role_synergy.append(synergy)
        parseMatchupsForRole(cur_proc_role, cur_role_synergy, synergies_df)

    return synergies_df


def parseMatchupsForRole(
    role: str, matchup_cells: list[PageElement], matchups_df: pd.DataFrame
) -> None:
    div_idx = {"wr": 0, "delta1": 1, "delta2": 2, "pr": 3, "games": 4}
    logger.info("Parsing Matchups for " + role)
    for matchup_cell in matchup_cells:
        champ = getChampName(matchup_cell)
        id = role + champ
        if id in matchups_df.index:
            print(champ + " already added to matchup dataframe")
            continue

        row: list[Any] = [id, role]
        row.append(champ)
        divs = matchup_cell.find_all_next("div")

        if len(divs) != len(div_idx):
            logger.error(
                "Invalid number of divs in the matchup celsl, could cause improper parsing"
            )
            logger.error("Exiting!")
            exit(-1)
        div_num = 0
        for div_num in range(0, len(div_idx)):
            # Convert div value to number
            if div_num != div_idx["games"]:
                val = float(divs[div_num].text.strip())
            else:
                div_text = divs[div_num].text.strip()
                div_text = "".join(div_text.split(","))
                val = int(div_text)
            row.append(val)
        matchups_df.loc[len(matchups_df.index)] = row


def getChampName(matchup_cell: PageElement) -> str:
    img_alt_text = str(matchup_cell.find_next("img", alt=True))
    champ_name = "".join(img_alt_text.split())  # Remove Spaces
    champ_name = "".join(champ_name.split("'"))  # Remove Apostrophes
    return champ_name.lower()  # Make all lower case
