import random
import csv
import numpy as np
from tabulate import tabulate
import math

MAX_OVERS = 20
TEAM_SIZE = 11
MAX_BOWLER_OVERS = 4
ROLE_LIMITS = {"Batsman": 5, "Allrounder": 1, "Wicketkeeper": 1, "Bowler": 4}




class Player:
    def __init__(self, raw_stats: dict):
        self.id = raw_stats["player_id"]
        self.name = raw_stats["name"]
        self.role = raw_stats["role"]
        self.batting_avg = raw_stats["batting_avg"]
        self.strike_rate = raw_stats["strike_rate"]
        self.boundary_pct = raw_stats["boundary_pct"]
        self.six_pct = raw_stats["six_pct"]
        self.bowling_econ = raw_stats["bowling_econ"]
        self.bowling_wicket_rate = raw_stats["bowling_wicket_rate"]
        self.extras_rate = raw_stats["extras_rate"]

        # Match state
        self.nerves = 0.20
        self.is_set = False
        self.match_runs_scored = 0
        self.match_balls_faced = 0
        self.match_wickets_taken = 0
        self.match_runs_conceded = 0
        self.match_balls_bowled = 0  
        self.balls_bowled_cap = 0   


class Ball:
    def __init__(self, extra: bool = False, wicket: bool = False, legal: bool = True, score: int = 0):
        self.extra = extra
        self.score = score
        self.wicket = wicket
        self.legal = legal


class Game:
    def __init__(self):
        self.teamscore = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0



def main():
    pool = get_team()
    if not pool:
        return
    team = choose_team(pool)
    innings(team)




def get_team() -> dict:
    """Load player pool from CSV, falling back to built-in sample data."""
    master_pool = {}
    try:
        with open("player_pool.csv", mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pid = row["player_id"]
                master_pool[pid] = {
                    "player_id": pid,
                    "name": row["name"],
                    "role": row["role"],
                    "batting_avg": float(row["batting_avg"]),
                    "strike_rate": float(row["strike_rate"]),
                    "boundary_pct": float(row["boundary_pct"]),
                    "six_pct": float(row["six_pct"]),
                    "bowling_econ": float(row["bowling_econ"]),
                    "bowling_wicket_rate": float(row["bowling_wicket_rate"]),
                    "extras_rate": float(row["extras_rate"]),
                }
    except FileNotFoundError:
        master_pool = _sample_pool()
    return master_pool


def _sample_pool() -> dict:
    rows = [
        {"player_id": "BAT_01", "name": "R. Sharma",  "role": "Batsman",     "batting_avg": 32.5, "strike_rate": 140.8, "boundary_pct": 62.1, "six_pct": 9.5,  "bowling_econ": 99.0, "bowling_wicket_rate": 0.0, "extras_rate": 0.0},
        {"player_id": "BAT_02", "name": "V. Kohli",   "role": "Batsman",     "batting_avg": 48.7, "strike_rate": 138.2, "boundary_pct": 51.4, "six_pct": 4.2,  "bowling_econ": 99.0, "bowling_wicket_rate": 0.0, "extras_rate": 0.0},
        {"player_id": "BAT_03", "name": "S. Gill",    "role": "Batsman",     "batting_avg": 29.4, "strike_rate": 135.5, "boundary_pct": 54.0, "six_pct": 5.1,  "bowling_econ": 99.0, "bowling_wicket_rate": 0.0, "extras_rate": 0.0},
        {"player_id": "BAT_04", "name": "Y. Jaiswal", "role": "Batsman",     "batting_avg": 36.2, "strike_rate": 160.3, "boundary_pct": 66.8, "six_pct": 11.2, "bowling_econ": 99.0, "bowling_wicket_rate": 0.0, "extras_rate": 0.0},
        {"player_id": "BAT_05", "name": "S. Iyer",    "role": "Batsman",     "batting_avg": 28.9, "strike_rate": 130.4, "boundary_pct": 49.5, "six_pct": 4.8,  "bowling_econ": 99.0, "bowling_wicket_rate": 0.0, "extras_rate": 0.0},
        {"player_id": "WK_01",  "name": "R. Pant",    "role": "Wicketkeeper","batting_avg": 30.1, "strike_rate": 126.5, "boundary_pct": 53.2, "six_pct": 6.4,  "bowling_econ": 99.0, "bowling_wicket_rate": 0.0, "extras_rate": 0.0},
        {"player_id": "AR_01",  "name": "H. Pandya",  "role": "Allrounder",  "batting_avg": 25.4, "strike_rate": 139.5, "boundary_pct": 55.2, "six_pct": 7.1,  "bowling_econ": 8.15, "bowling_wicket_rate": 5.2, "extras_rate": 3.1},
        {"player_id": "BOWL_01","name": "J. Bumrah",  "role": "Bowler",      "batting_avg": 7.2,  "strike_rate": 85.0,  "boundary_pct": 20.0, "six_pct": 0.5,  "bowling_econ": 6.25, "bowling_wicket_rate": 6.8, "extras_rate": 2.1},
        {"player_id": "BOWL_02","name": "K. Yadav",   "role": "Bowler",      "batting_avg": 6.5,  "strike_rate": 70.0,  "boundary_pct": 15.0, "six_pct": 0.0,  "bowling_econ": 6.75, "bowling_wicket_rate": 5.8, "extras_rate": 3.4},
        {"player_id": "BOWL_03","name": "M. Siraj",   "role": "Bowler",      "batting_avg": 5.1,  "strike_rate": 65.0,  "boundary_pct": 10.0, "six_pct": 0.0,  "bowling_econ": 8.45, "bowling_wicket_rate": 5.1, "extras_rate": 4.2},
        {"player_id": "BOWL_04","name": "A. Singh",   "role": "Bowler",      "batting_avg": 5.5,  "strike_rate": 75.0,  "boundary_pct": 12.0, "six_pct": 0.2,  "bowling_econ": 8.20, "bowling_wicket_rate": 5.5, "extras_rate": 4.8},
    ]
    return {r["player_id"]: r for r in rows}


def choose_team(pool: dict) -> list:
    """Select an 11-player team respecting role quotas."""
    team, counts = [], {role: 0 for role in ROLE_LIMITS}
    for player_data in pool.values():
        role = player_data["role"]
        if role in counts and counts[role] < ROLE_LIMITS[role]:
            team.append(Player(player_data))
            counts[role] += 1
        if len(team) == TEAM_SIZE:
            break
    return team




def innings(team: list):
    game = Game()
    context = {
        "lineup": team,
        "striker": team[0],
        "non_striker": team[1],
        "next_batsman_idx": 2,
        "bowlers_pool": [p for p in team if p.role in ("Bowler", "Allrounder")],
        "last_bowler": None,
        "last_ball_outcome": "0", 
    }

    for _ in range(MAX_OVERS):
        if game.wickets == 10:
            break
        bowl_over(game, context)
        game.overs += 1

    print(f"\nFinal Score: {game.teamscore}/{game.wickets} in {game.overs} overs\n")
    display_card(team, context["bowlers_pool"])


def _pick_bowler(context: dict) -> Player:
    CAP_BALLS = MAX_BOWLER_OVERS * 6  # 24
    pool = context["bowlers_pool"]
    last = context["last_bowler"]

    eligible = [b for b in pool if b.balls_bowled_cap < CAP_BALLS and b is not last]
    if not eligible:
        eligible = [b for b in pool if b.balls_bowled_cap < CAP_BALLS]
    if not eligible:
        eligible = pool

    return random.choice(eligible)


def bowl_over(game: Game, context: dict):
    bowler = _pick_bowler(context)
    context["last_bowler"] = bowler
    legal_balls = 0

    while legal_balls < 6:
        if game.wickets == 10:
            break
        ball = play_ball(bowler, context, game)
        if ball.legal:
            legal_balls += 1
            game.balls += 1

    context["striker"], context["non_striker"] = context["non_striker"], context["striker"]

def play_ball(bowler: Player, context: dict, game: Game) -> Ball:
    striker = context["striker"]
    ball = simulate_ball(bowler, striker)

    if ball.wicket:
        context["last_ball_outcome"] = "W"
        game.wickets += 1
        bowler.match_wickets_taken += 1
        bowler.balls_bowled_cap += 1
        striker.is_set = False
        _bring_in_next_batsman(context, game)
        return ball

    if ball.extra:
        context["last_ball_outcome"] = "E"
        game.teamscore += ball.score
        bowler.match_runs_conceded += ball.score
        return ball

    context["last_ball_outcome"] = str(ball.score)
    game.teamscore += ball.score
    striker.match_runs_scored += ball.score
    striker.match_balls_faced += 1
    bowler.match_runs_conceded += ball.score
    bowler.match_balls_bowled += 1
    bowler.balls_bowled_cap += 1

    if striker.match_balls_faced >= 10:
        striker.is_set = True

    if ball.score in (1, 3):
        _rotate_strike(context)

    return ball


def _bring_in_next_batsman(context: dict, game: Game):
    if game.wickets < 10:
        context["striker"] = context["lineup"][context["next_batsman_idx"]]
        context["next_batsman_idx"] += 1


def _rotate_strike(context: dict):
    context["striker"], context["non_striker"] = context["non_striker"], context["striker"]


def simulate_ball(bowler: Player, batsman: Player) -> Ball:
    sr_factor       = batsman.strike_rate / 100
    avg_factor      = batsman.batting_avg / 100
    boundary_factor = (batsman.boundary_pct / 100 * 4) + (batsman.six_pct / 100 * 6)
    matchup_factor  = (sr_factor+avg_factor) - (bowler.bowling_econ+ bowler.bowling_wicket_rate / 10)-batsman.nerves

    lam = (sr_factor + avg_factor + boundary_factor + matchup_factor) / 4 + (2+3+4+6)/6


    lam = max(0.3, min(4.5, lam))

    run_weights = get_weights(lam)
    wicket_prob = (bowler.bowling_wicket_rate / 100) * (0.8 + batsman.nerves)
    extra_prob  = bowler.extras_rate / 100

    outcomes    = [0, 1, 2, 3, 4, 6, "W", "E"]
    all_weights = np.append(run_weights, [wicket_prob, extra_prob])
    all_weights /= all_weights.sum()

    result = random.choices(outcomes, weights=all_weights.tolist())[0]

    if result == "E":
        return Ball(extra=True, legal=False, score=1)

    if result == "W":
        batsman.nerves = min(0.60, batsman.nerves + 0.10)
        return Ball(wicket=True, legal=True, score=0)

    if result == 0:
        batsman.nerves = min(0.60, batsman.nerves + 0.02)
    elif result == 4:
        batsman.nerves = max(0.05, batsman.nerves - 0.04)
    elif result == 6:
        batsman.nerves = max(0.05, batsman.nerves - 0.08)

    return Ball(score=result, legal=True)


def get_weights(lam: float) -> np.ndarray:
    indices    = np.arange(7)
    factorials = np.array([math.factorial(i) for i in indices])
    pmf        = (np.exp(-lam) * (lam ** indices)) / factorials
    return np.array([
        pmf[0], pmf[1], pmf[2] + pmf[3]/4, pmf[3]/8,
        pmf[4] + pmf[5] * 0.5 + pmf[3]/2,
        pmf[6] + pmf[5] * 0.5 + pmf[3]/8,
    ])



def display_card(batting_team: list, bowling_team: list):
    bat_rows = []
    for p in batting_team:
        sr = (p.match_runs_scored / p.match_balls_faced * 100) if p.match_balls_faced > 0 else 0.0
        bat_rows.append([p.name, p.match_runs_scored, p.match_balls_faced, f"{sr:.2f}"])

    bowl_rows = []
    for p in bowling_team:
        if p.balls_bowled_cap > 0:
            total_legal = p.balls_bowled_cap
            overs_str = f"{total_legal // 6}.{total_legal % 6}"
            econ = (p.match_runs_conceded / p.match_balls_bowled * 6) if p.match_balls_bowled > 0 else 0.0
            bowl_rows.append([p.name, overs_str, p.match_runs_conceded, p.match_wickets_taken, f"{econ:.2f}"])

    print("\n--- BATTING SCORECARD ---")
    print(tabulate(bat_rows, headers=["Batsman", "Runs", "Balls", "SR"], tablefmt="grid"))
    print("\n--- BOWLING SCORECARD ---")
    print(tabulate(bowl_rows, headers=["Bowler", "Overs", "Runs", "Wickets", "Econ"], tablefmt="grid"))


if __name__ == "__main__":
    main()