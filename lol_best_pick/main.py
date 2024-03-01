import argparse

import yaml

from lol_best_pick import analysis, parse_lolalytics, web_scraping
from lol_best_pick.util import PROJECT_ROOT_DIR


def update(config_path: str) -> None:
    with open(config_path, "r") as config_yaml:
        champ_pool = yaml.safe_load(config_yaml)["champ_pool"]
    web_scraping.fetchLolalytics(champ_pool, force=False)
    parse_lolalytics.parseLolalytics(champ_pool, force=False)


def best_pick(config_path: str) -> None:
    with open(config_path, "r") as config_yaml:
        config = yaml.safe_load(config_yaml)
        my_role = config["my_role"]
        champ_pool = config["champ_pool"]
        bans = config["bans"]
        enemy_team = config["bans"]
        ally_team = config["bans"]

    analysis.bestPick(my_role, bans, champ_pool, enemy_team, ally_team)


if __name__ == "__main__":
    with open(f"{PROJECT_ROOT_DIR}/configs/config_picker.yml", "r") as file:
        config_picker_yaml = yaml.safe_load(file)
        config_path = PROJECT_ROOT_DIR + "/" + config_picker_yaml["path"]

    parser = argparse.ArgumentParser(
        prog="Best Matchup",
        description="Based on the champions picked already in your lobby, find the best champion "
        "choice within your champion pool.",
    )
    parser.add_argument("-u", "--update", action="store_true")
    args = parser.parse_args()
    if args.update:
        update(config_path)
    else:
        best_pick(config_path)
