import pandas as pd
import math
from util import getMatchupCSVPath, getSynergyCSVPath, cleanString


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def removeUnavailableChampions(
    my_role_pool: list[str],
    bans: list[str],
    enemy_team_champs: list[str],
    ally_team_champs: list[str],
):
    available_champions: list[str] = []
    for champ in my_role_pool:
        banned = champ in bans
        on_their_team = champ in enemy_team_champs
        on_my_team = champ in ally_team_champs
        if not (banned or on_their_team or on_my_team):
            available_champions.append(champ)
    return available_champions


def cleanChampNamesDict(
    champs: dict[str, str],
):
    cleaned: dict[str, str] = {}
    for role, name in champs.items():
        cleaned[role] = cleanString(name)
    return cleaned


def cleanChampNamesList(
    champs: list[str],
):
    cleaned: list[str] = []
    for name in champs:
        cleaned.append(cleanString(name))
    return cleaned


def matchupExists(matchup_df, my_champ, other_champ, role):
    matchup_exists = matchup_df.shape[0] != 0
    if not matchup_exists:
        print(
            f"Matchup not found: {my_champ.capitalize()} vs "
            + f"{other_champ.capitalize()} {role}"
        )
    return matchup_exists


def sufficientGames(matchup_df, my_champ, other_champ, role):
    num_games = matchup_df.loc[0]["games"]
    sufficient_quantity = num_games >= 33
    if not sufficient_quantity:
        print(
            f"Insufficent matchup games({num_games}): "
            + f"{my_champ.capitalize()} vs {other_champ.capitalize()}"
            + f" {role}"
        )
    return sufficient_quantity


def bestPick(
    my_role: str,
    bans: list[str],
    my_pool: dict[str, list[str]],
    enemy_team: dict[str, str],
    ally_team: dict[str, str],
):
    summary_columns = ["my_champ", "total_score", "mean_wr", "mean_delta2"]
    summarized = pd.DataFrame(columns=summary_columns)

    my_pool[my_role] = cleanChampNamesList(my_pool[my_role])
    bans = cleanChampNamesList(bans)
    enemy_team = cleanChampNamesDict(enemy_team)
    ally_team = cleanChampNamesDict(ally_team)

    my_pool[my_role] = removeUnavailableChampions(
        my_pool[my_role],
        bans,
        list(enemy_team.values()),
        list(ally_team.values()),
    )

    for my_champ in my_pool[my_role]:
        skipped = 0
        print("\n" + my_champ.upper() + " " + my_role.upper())
        # MATCHUPS -------------------------------------------------------------------------------
        all_matchups_df = pd.read_csv(getMatchupCSVPath(my_role, my_champ))
        game_matchups = []
        for enemy_role, enemy_champ in enemy_team.items():
            # Skip unitialized entries
            if enemy_champ == None or enemy_champ == "":
                continue

            # Try to pull matchup data from table
            matchup_df = getWithChampDf(all_matchups_df, enemy_champ, enemy_role)

            if not matchupExists(
                matchup_df, my_champ, enemy_champ, enemy_role
            ) or not sufficientGames(matchup_df, my_champ, enemy_champ, enemy_role):
                wr = 50.0
                delta1 = 0.00
                delta2 = 0.00
            else:
                wr = matchup_df.loc[0]["wr"]
                delta1 = matchup_df.loc[0]["delta1"]
                delta2 = matchup_df.loc[0]["delta2"]

            score = calcScore(my_role, enemy_role, delta2)
            game_matchups.append(
                [my_champ, "vs", enemy_champ, enemy_role, score, wr, delta1, delta2]
            )

        # SYNERGIES ------------------------------------------------------------------------------
        all_synergies_df = pd.read_csv(getSynergyCSVPath(my_role, my_champ))
        game_synergies = []
        for ally_role, ally_champ in ally_team.items():
            # Skip unitialized entries
            if ally_champ == None or ally_champ == "":
                continue

            # Try to pull matchup data from table
            synergy_df = getWithChampDf(all_synergies_df, ally_champ, ally_role)

            if not matchupExists(
                matchup_df, my_champ, ally_champ, ally_role
            ) or not sufficientGames(matchup_df, my_champ, ally_champ, ally_role):
                wr = 0.50
                delta1 = 0.00
                delta2 = 0.00
            else:
                wr = synergy_df.loc[0]["wr"]
                delta1 = synergy_df.loc[0]["delta1"]
                delta2 = synergy_df.loc[0]["delta2"]

            score = calcScore(my_role, ally_role, delta2)

            game_synergies.append(
                [
                    my_champ,
                    "with",
                    ally_champ,
                    ally_role,
                    score,
                    wr,
                    delta1,
                    delta2,
                ]
            )

        columns = [
            "my_champ",
            "relation",
            "their_champ",
            "their_role",
            "score",
            "wr",
            "delta1",
            "delta2",
        ]
        print(f"Matchup Data {'-'*60}")
        matchups_df = pd.DataFrame(game_matchups, columns=columns)
        print(matchups_df)
        print(f"Synergy Data {'-'*60}")
        synergies_df = pd.DataFrame(game_synergies, columns=columns)
        print(synergies_df)

        total_score = pd.concat([matchups_df["score"], synergies_df["score"]]).sum()

        mean_wr = pd.concat([matchups_df["wr"], synergies_df["wr"]]).mean()
        mean_delta2 = pd.concat([matchups_df["delta2"], synergies_df["delta2"]]).mean()
        row = [my_champ, total_score, mean_wr, mean_delta2]
        summarized.loc[-1] = row  # adding a row
        summarized.index = summarized.index + 1  # shifting index

    print("\n" + "-" * 55)
    print(" SUMMARIZED BEST PICK DATA (Highest Score = Best Pick)")
    print("-" * 55)
    print(summarized.sort_values(by=["total_score"]))


def getWithChampDf(with_champ_df: pd.DataFrame, their_champ: str, their_role: str):
    df = with_champ_df.loc[with_champ_df["role"] == their_role]
    df = df.loc[df["champ"] == their_champ]
    df.reset_index(drop=True, inplace=True)
    return df


def calcScore(my_role, enemy_role, metric):
    TOP, JUNGLE, MIDDLE, BOTTOM, SUPPORT = 0, 1, 2, 3, 4
    if enemy_role == "top":
        scaling_idx = TOP
    elif enemy_role == "jungle":
        scaling_idx = JUNGLE
    elif enemy_role == "middle":
        scaling_idx = MIDDLE
    elif enemy_role == "bottom":
        scaling_idx = BOTTOM
    elif enemy_role == "support":
        scaling_idx = SUPPORT

    if my_role == "top":
        scale_values = [1.00, 0.50, 0.33, 0.25, 0.25]
    elif my_role == "jungle":
        scale_values = [0.35, 1.00, 0.50, 0.25, 0.35]
    elif my_role == "middle":
        scale_values = [0.10, 0.35, 1.00, 0.10, 0.25]
    elif my_role == "bottom":
        scale_values = [0.10, 0.50, 0.33, 1.00, 1.00]
    elif my_role == "support":
        scale_values = [0.30, 0.65, 0.50, 1.00, 1.00]

    scaled_score = sigmoid(metric) * scale_values[scaling_idx]
    scaled_average_score = 0.5 * scale_values[scaling_idx]

    return round((scaled_score - scaled_average_score) * 100)
