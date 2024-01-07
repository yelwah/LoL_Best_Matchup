import re, os
from bs4 import BeautifulSoup
from global_logger import logger
import pandas as pd
from util import needsUpdate, getMatchupHTMLSavePath, getSynergyHTMLSavePath, getMatchupCSVPath, \
  getSynergyCSVPath, cleanString
ROLES = ["top", "jungle", "middle", "bottom", "support"]
stat_types = ["wr", "delta1", "delta2", "pr", "games"]

def parseLolalytics(pool:dict[str, list[str]], force:bool = False):
  print("\n Parsing newly updated matchup data from Lolalytics\n" + ("*" * 80))
  at_least_one_parsed = False
  for my_role, my_champs in pool.items():
    for champ in my_champs:
      # Fix up the string to be all lower no apostophes
      cleanString(champ)
      
      # If necessary, parse the matchup data for this champion in this role
      matchup_csv_path = getMatchupCSVPath(my_role, champ)
      matchup_html_path = getMatchupHTMLSavePath(my_role, champ)

      if os.path.exists(matchup_html_path) and (needsUpdate(matchup_csv_path, 1) or force):
        at_least_one_parsed = True
        # Print which Champion is being Parsed
        logger.info("PARSING DATA FOR " + champ.upper() + " " + my_role.upper())
      
        # Load the Matchup HTML page from file
        with open(matchup_html_path, encoding="utf-8") as fp:
          matchup_soup = BeautifulSoup(fp, 'lxml')
        print(f"os.remove({matchup_html_path})")
        os.remove(matchup_html_path)
        matchups_df = getMatchupsDataFrame(matchup_soup)

        matchups_df.to_csv(matchup_csv_path)
      
      # If necessary, parse the synergy data for this champion in this role
      synergy_csv_path = getSynergyCSVPath(my_role, champ)
      synergy_html_path = getSynergyHTMLSavePath(my_role, champ)

      if os.path.exists(synergy_html_path) and (needsUpdate(synergy_csv_path, 1) or force):
        at_least_one_parsed = True
        # Load the Synergy HTML page from file
        with open(synergy_html_path, encoding="utf-8") as fp:
          synergy_soup = BeautifulSoup(fp, 'lxml')
        print(f"os.remove({synergy_html_path})")
        os.remove(synergy_html_path)
        synergies_df = getSynergiesDataFrame(synergy_soup)

        synergies_df.to_csv(synergy_csv_path)
  if not at_least_one_parsed:
    print("All current matchups and synergies are already parsed.")
  print("\nParsing complete.\n")

def getMatchupsDataFrame(matchup_soup:BeautifulSoup):
  matchups_df = pd.DataFrame(columns=(["id", "role", "champ"] + stat_types))
  matchups_df.set_index("id")

  for cur_proc_role in ROLES:
    print("Finding matchups for " + str(cur_proc_role))
    matchup_cells = matchup_soup.find_all("div", {"class": "Cell_cell__383UV"})
    cur_role_matchups = []
    for matchup in matchup_cells:
      regex = re.compile(r".+vslane=" + cur_proc_role)
      if matchup.find('a', href = regex) != None:
        cur_role_matchups.append(matchup)
    parseMatchupsForRole(cur_proc_role, cur_role_matchups, matchups_df)

  return matchups_df

def getSynergiesDataFrame(synergy_soup:BeautifulSoup):
  synergies_df = pd.DataFrame(columns=(["id", "role", "champ"] + stat_types))
  synergies_df.set_index("id")

  for cur_proc_role in ROLES:
    print("Finding synergies for " + str(cur_proc_role))
    synergy_cells = synergy_soup.find_all("div", {"class": "Cell_cell__383UV"})
    cur_role_synergy = []
    for synergy in synergy_cells:
      regex = re.compile(r".+lane=" + cur_proc_role)
      if synergy.find('a', href = regex) != None:
        cur_role_synergy.append(synergy)
    parseMatchupsForRole(cur_proc_role, cur_role_synergy, synergies_df)
  
  return synergies_df

def parseMatchupsForRole(role:str, matchup_cells:BeautifulSoup, matchups_df:pd.DataFrame):
  WR = 0
  DELTA1 = 1
  DELTA2 = 2
  PR = 3
  GAMES = 4
  logger.info("Parsing Matchups for " + role)
  for matchup_cell in matchup_cells:
    champ = getChampName(matchup_cell)
    id = role + champ
    if (id in matchups_df.index):
      print(champ + " already added to matchup dataframe")
      continue

    row = [id, role]
    row.append(champ)
    divs = matchup_cell.find_all("div")
    
    if len(divs) != 5:
      logger.error("Invalid number of divs in the matchup cell, could cause improper parsing")
      logger.error("Exiting!")
      exit(-1)
    div_num = 0
    for div in divs:
      # Convert div value to number
      if div_num != GAMES:
        val = float(div.text.strip())
      else:
        div_text = div.text.strip()
        div_text = "".join(div_text.split(','))
        val = int(div_text)
      row.append(val)
      div_num += 1
    matchups_df.loc[len(matchups_df.index)] = row

def getChampName(matchup_cell:BeautifulSoup):
    img = matchup_cell.find('img', alt=True)      # Pull alt text from champion image
    champ_name = "".join(img['alt'].split())      # Remove Spaces
    champ_name = "".join(champ_name.split('\''))  # Remove Apostrophes
    champ_name = champ_name.lower()               # Make all lower case
    return champ_name