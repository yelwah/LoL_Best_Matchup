import pandas as pd
import math
from global_logger import logger
from util import getMatchupCSVPath, getSynergyCSVPath, cleanString


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def removeUnavailableChampions(
    my_role_pool: list[str],
    bans: list[str],
    enemy_team_champs: list[str],
    ally_team_champs: list[str],
):
    """"""
    available_champions:list[str] = []
    for champ in my_role_pool:
        banned = champ in bans
        on_their_team = champ in enemy_team_champs
        on_my_team = champ in ally_team_champs
        if not (banned or on_their_team or on_my_team):
            available_champions += champ
    my_role_pool = available_champions


def bestPick(
    my_role: str,
    bans: list[str],
    my_pool: dict[str, list[str]],
    enemy_team: dict[str, str],
    ally_team: dict[str, str],
):
    summary_columns = ["my_champ", "total_score", "mean_wr", "mean_delta2"]
    summarized = pd.DataFrame(columns=summary_columns)

    removeUnavailableChampions(
        my_pool[my_role],
        bans,
        list(enemy_team.values()),
        list(ally_team.values()),
    )

    temp = []
    for champ in my_pool[my_role]:
        on_my_team = False
        for role, ally_champ in ally_team.items():
            if champ == ally_champ:
                on_my_team = True

        if (
            (not on_my_team)
            and (champ not in enemy_team[my_role])
            and (champ not in bans)
        ):
            temp.append(champ)

    my_pool[my_role] = temp

    for my_champ in my_pool[my_role]:
        skipped = 0
        # Fix up the string to be all lower no apostophes
        cleanString(my_champ)
        logger.debug("my_champ=" + my_champ + ", my_role=" + my_role)
        print("\n" + my_champ.upper() + " " + my_role.upper())
        # MATCHUPS -------------------------------------------------------------------------------------
        all_matchups_df = pd.read_csv(getMatchupCSVPath(my_role, my_champ))
        game_matchups = []
        for enemy_role, enemy_champ in enemy_team.items():
            # Skip unitialized entries, clean the champ name string for valid entries
            if enemy_champ != None and enemy_champ != "":
                cleanString(enemy_champ)
                logger.debug(
                    ".. enemy_role="
                    + enemy_role
                    + ", enemy_champ="
                    + enemy_champ
                )
            else:
                continue

            # Do not process mirror matchups
            if my_champ == enemy_champ:
                logger.debug("skipping mirror matchup")
                skipped += 1
                continue

            # Try to pull matchup data from table (we check if we got anything next)
            matchup_df = getWithChampDf(
                all_matchups_df, enemy_champ, enemy_role
            )
            # If matchup data doesn't exist, ignore
            if matchup_df.shape[0] == 0:
                print(
                    "Matchup not found: "
                    + my_champ.capitalize()
                    + " vs "
                    + enemy_champ.capitalize()
                    + " "
                    + enemy_role
                )
                skipped += 1
                continue
            # Else if there are not sufficent games to be accurately analyzed, ignore
            elif matchup_df.loc[0]["games"] < 50:
                print(
                    "Insufficent matchup games("
                    + str(matchup_df.loc[0]["games"])
                    + "): "
                    + my_champ.capitalize()
                    + " vs "
                    + enemy_champ.capitalize()
                    + " "
                    + enemy_role
                )
                skipped += 1
                continue

            wr = matchup_df.loc[0]["wr"]
            delta1 = matchup_df.loc[0]["delta1"]
            delta2 = matchup_df.loc[0]["delta2"]
            score = calcScore(my_role, enemy_role, delta2)
            game_matchups.append(
                [
                    my_champ,
                    "vs",
                    enemy_champ,
                    enemy_role,
                    score,
                    wr,
                    delta1,
                    delta2,
                ]
            )

        # SYNERGIES ------------------------------------------------------------------------------------
        all_synergies_df = pd.read_csv(getSynergyCSVPath(my_role, my_champ))
        game_synergies = []
        for ally_role, ally_champ in ally_team.items():
            # Skip unitialized entries, clean the champ name string for valid entries
            if ally_champ != None and ally_champ != "":
                cleanString(ally_champ)
            else:
                continue

            logger.debug(
                ".. ally_role=" + ally_role + ", ally_champ=" + ally_champ
            )

            # Try to pull matchup data from table (we check if we got anything next)
            synergy_df = getWithChampDf(all_synergies_df, ally_champ, ally_role)
            # If matchup data doesn't exist, ignore
            if synergy_df.shape[0] == 0:
                print(
                    "Synergy not found: "
                    + my_champ.capitalize()
                    + " with "
                    + ally_champ.capitalize()
                    + " "
                    + ally_role
                )
                skipped += 1
                wr = 50.0
                delta1 = 0.0
                delta2 = 0.0
            # Else if there are not sufficent games to be accurately analyzed, ignore
            elif synergy_df.loc[0]["games"] < 50:
                print(
                    "Insufficent synergy games("
                    + str(synergy_df.loc[0]["games"])
                    + "): "
                    + my_champ.capitalize()
                    + " with "
                    + ally_champ.capitalize()
                    + " "
                    + ally_role
                )
                skipped += 1
                wr = 50.0
                delta1 = 0.0
                delta2 = 0.0
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
        print(
            "Matchup Data ------------------------------------------------------------------"
        )
        matchups_df = pd.DataFrame(game_matchups, columns=columns)
        print(matchups_df)
        print(
            "Synergy Data ------------------------------------------------------------------"
        )
        synergies_df = pd.DataFrame(game_synergies, columns=columns)
        print(synergies_df)

        total_score = pd.concat(
            [matchups_df["score"], synergies_df["score"]]
        ).sum()
        if skipped != 0:
            print(
                str(skipped)
                + " matchup/synergy skipped for "
                + my_champ.capitalize()
                + ".\n"
                + "(Skipped synergies are counted as an even matchup for score (50), and are omitted from means)"
            )
            total_score += score

        mean_wr = pd.concat([matchups_df["wr"], synergies_df["wr"]]).mean()
        mean_delta1 = pd.concat(
            [matchups_df["delta1"], synergies_df["delta1"]]
        ).mean()
        row = [my_champ, total_score, mean_wr, mean_delta1]
        summarized.loc[-1] = row  # adding a row
        summarized.index = summarized.index + 1  # shifting index

    print("\n" + "-" * 80)
    print("SUMMARIZED BEST PICK DATA (Highest Score = Best Pick)")
    print("-" * 80)
    print(summarized.sort_values(by=["total_score"]))


def getWithChampDf(
    with_champ_df: pd.DataFrame, their_champ: str, their_role: str
):
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
        scale_values = [1, 0.5, 0.33, 0.25, 0.25]
    elif my_role == "jungle":
        scale_values = [0.35, 1, 0.5, 0.25, 0.35]
    elif my_role == "middle":
        scale_values = [0.1, 0.35, 1, 0.1, 0.25]
    elif my_role == "bottom":
        scale_values = [0.1, 0.5, 0.33, 1, 1]
    elif my_role == "support":
        scale_values = [0.3, 0.65, 0.5, 1, 1]

    logger.debug(
        "roleDelta2Scaling(): my_role="
        + my_role
        + ", enemy_role="
        + enemy_role
        + ", delta1="
        + str(metric)
    )
    logger.debug("... scale_index=" + str(scaling_idx))
    logger.debug("... scaling_values=" + str(scale_values))
    logger.debug(
        "... calculated scaling to be " + str(scale_values[scaling_idx])
    )
    logger.debug("... scaled_delta1=" + str(metric * scale_values[scaling_idx]))
    logger.debug(
        "... normalized_scaled_delta1(score)="
        + str(sigmoid(metric * scale_values[scaling_idx]))
    )
    return round(sigmoid(metric) * scale_values[scaling_idx] * 100)
