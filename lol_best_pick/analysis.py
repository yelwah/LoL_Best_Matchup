import math

import pandas as pd

from .util import cleanString, getMatchupCSVPath, getSynergyCSVPath


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def removeUnavailableChampions(
    my_role_pool: list[str],
    bans: list[str],
    enemy_team_champs: list[str],
    ally_team_champs: list[str],
) -> list[str]:
    available_champions: list[str] = []
    for champ in my_role_pool:
        banned = champ in bans
        on_their_team = champ in enemy_team_champs
        on_my_team = champ in ally_team_champs
        if not (banned or on_their_team or on_my_team):
            available_champions.append(champ)
    return available_champions


def cleanChampNamesDict(
    champs: dict[str, str] | None,
) -> dict[str, str]:
    if champs is None:
        return {}
    cleaned: dict[str, str] = {}
    for role, name in champs.items():
        cleaned[role] = cleanString(name)
    return cleaned


def cleanChampNamesList(
    champs: list[str] | None,
) -> list[str]:
    if champs is None:
        return []
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


def filtedValidMatches(all_entries_df, team, my_champ, my_role):
    valid_entries = []
    for role, champ in team.items():
        # Skip unitialized entries
        if champ is None or champ == "":
            continue

        # Try to pull matchup data from table
        matchup_df = getWithChampDf(all_entries_df, champ, role)

        if not matchupExists(matchup_df, my_champ, champ, role) or not sufficientGames(
            matchup_df, my_champ, champ, role
        ):
            wr = 50.0
            delta1 = 0.00
            delta2 = 0.00
        else:
            wr = matchup_df.loc[0]["wr"]
            delta1 = matchup_df.loc[0]["delta1"]
            delta2 = matchup_df.loc[0]["delta2"]

        score1 = calcScore(my_role, role, delta1)
        score2 = calcScore(my_role, role, delta2)
        valid_entries.append(
            [my_champ, "and", champ, role, score1, score2, wr, delta1, delta2]
        )
    return valid_entries


def bestPick(
    my_role: str,
    bans: list[str],
    my_pool: dict[str, list[str]],
    enemy_team: dict[str, str],
    ally_team: dict[str, str],
) -> None:
    summary_columns = [
        "my_champ",
        "sc1",
        "sc2",
        "∑sc",
        "wr",
        "Δ1",
        "Δ2",
    ]
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
        print("\n" + my_champ.upper() + " " + my_role.upper())
        # MATCHUPS -------------------------------------------------------------------------------
        all_matchups_df = pd.read_csv(getMatchupCSVPath(my_role, my_champ))
        game_matchups = filtedValidMatches(
            all_matchups_df, enemy_team, my_champ, my_role
        )

        # SYNERGIES ------------------------------------------------------------------------------
        all_synergies_df = pd.read_csv(getSynergyCSVPath(my_role, my_champ))
        game_synergies = filtedValidMatches(
            all_synergies_df, ally_team, my_champ, my_role
        )

        columns = ["", "", "", "", "score1", "score2", "wr", "delta1", "delta2"]
        print(f"Matchup Data {'-'*60}")
        matchups_df = pd.DataFrame(game_matchups, columns=columns)
        print(matchups_df)
        print(f"Synergy Data {'-'*60}")
        synergies_df = pd.DataFrame(game_synergies, columns=columns)
        print(synergies_df)

        total_score1 = pd.concat([matchups_df["score1"], synergies_df["score1"]]).sum()
        total_score2 = pd.concat([matchups_df["score2"], synergies_df["score2"]]).sum()
        total_score_sum = pd.concat(
            [
                matchups_df["score1"],
                synergies_df["score1"],
                matchups_df["score2"],
                synergies_df["score2"],
            ]
        ).sum()
        mean_wr = pd.concat([matchups_df["wr"], synergies_df["wr"]]).mean()
        mean_delta1 = pd.concat([matchups_df["delta1"], synergies_df["delta1"]]).mean()
        mean_delta2 = pd.concat([matchups_df["delta2"], synergies_df["delta2"]]).mean()
        row = [
            my_champ,
            total_score1,
            total_score2,
            total_score_sum,
            mean_wr,
            mean_delta1,
            mean_delta2,
        ]
        summarized.loc[-1] = row  # adding a row
        summarized.index = summarized.index + 1  # shifting index

    print("\nMAX MID SCORES RANGE -180 <---> 180")
    print("-" * 75)
    print(" SUMMARIZED BEST PICK DATA (Highest Score = Best Pick)")
    print("-" * 75)
    print(summarized.sort_values(by=["∑sc"]))


def getWithChampDf(
    with_champ_df: pd.DataFrame, their_champ: str, their_role: str
) -> pd.DataFrame:
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
    return round((scaled_score - scaled_average_score) * 100)
