"""
CLI script to measure and compare performance of Mathematico agents
===================================================================

This script can be used to compare different (previously measured)
Mathematico agents, or to measure a new one.

To just display the results, do not include options --file or --cls.


Sorting
-------
    The results are sorted based on one of the following criteria:
        * average score [--sort-by-score]: based on the average score
          obtained in the sampled games

        * score gain / time [--sort-by-time-score]: estimates the performance
          GAIN against the random player per one second of computation;

        * tournament score [--sort-by-tournament]: for each of the simulated
          rounds, ranks the available agents, the WINNER obtains score of
          `len(agents) - 1`, each consecutive placement obtains one point less,
          the last player is awarded 0 points; the final score is averaged
          over all rounds. Default.
"""
import argparse
import importlib.util
import multiprocessing
import os
import statistics
import sys
import time
from dataclasses import dataclass
from enum import Enum
from itertools import count, repeat
from typing import Callable, List

from mathematico import Mathematico
from tabulate import tabulate
from tqdm import tqdm

################################################################################
##  Constants
################################################################################

GAMES = 20
SEED = 696969
SEEDS = [i for i in range(SEED, SEED+GAMES)]
DB_FILE = "./data.csv"
RANDOM_SCORE = 83.7
EPS = 1e-5


@dataclass
class Record:
    name: str
    file: str
    desc: str
    points: List[float]
    avg_time: float

    def format(self) -> str:
        name = self.name.replace(",", ";")
        desc = self.desc.replace(",", ";")
        pts = ",".join(map(str, self.points))
        tim = str(self.avg_time)
        return f"{name},{self.file},{desc},{pts},{tim}"

    @classmethod
    def load(cls, s: str) -> 'Record':
        name, file, desc, *_scores, _avg_time = s.split(",")
        scores = list(map(float, _scores))
        avg_time = float(_avg_time)
        return cls(name, file, desc, scores, avg_time)


class Ranking(Enum):
    BY_SCORE = 0
    BY_SCORE_PER_TIME = 1
    BY_TOURNAMENT = 2



################################################################################
##  DB stuff
################################################################################

def _store_data(data: Record):
    with open(DB_FILE, "+a", encoding="utf-8") as f:
        f.write(data.format() + "\n")


def _load_data() -> List[Record]:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return list(map(Record.load, f))


################################################################################
##  Presentation
################################################################################

def _tournament_rankings(data: List[Record]) -> List[float]:
    if not data:
        return []

    ranks = [0 for _ in range(len(data))]
    ROUNDS = len(data[0].points)

    for round in range(ROUNDS):
        for player in range(len(data)):
            smaller_eq_cnt = 0
            for other in range(len(data)):
                if data[player].points[round] >= data[other].points[round]:
                    smaller_eq_cnt += 1
            ranks[player] += smaller_eq_cnt
    return [score/(ROUNDS * len(data)) for score in ranks]


def _avg_score_rankings(data: List[Record]) -> List[float]:
    return [statistics.mean(d.points) for d in data]


def _score_per_time_rankings(data: List[Record]) -> List[float]:
    scores = _avg_score_rankings(data)
    return [(s - RANDOM_SCORE) / (d.avg_time + EPS) for s, d in zip(scores, data)]


def _corr(method: Callable, a, b):
    result = method(a, b)
    return result.statistic, result.pvalue


def _prep_data(data: List[Record], rank: Ranking, do_corr=False):
    headers = [
        "name", "file", "description", "avg_score",
        "time", "score gain/time", "tournament"
    ]

    avg_score = _avg_score_rankings(data)
    score_time = _score_per_time_rankings(data)
    tourn = _tournament_rankings(data)
    order_by = 0  # by name

    match rank:
        case Ranking.BY_SCORE:
            order_by = 3
        case Ranking.BY_SCORE_PER_TIME:
            order_by = 5
        case Ranking.BY_TOURNAMENT:
            order_by = 6
        case _:
            assert False

    _data = [
        (d.name, d.file, d.desc, score, d.avg_time, st, tour)
        for d, score, st, tour in zip(data, avg_score, score_time, tourn)
    ]

    _data.sort(key=lambda r: r[order_by], reverse=True)

    if do_corr:
        import scipy

        print("Correlations analysis (coef, p-value):")
        print("=====================================")

        print("Score vs Tournament")
        print(f"\tSpearman: {_corr(scipy.stats.spearmanr, avg_score, tourn)}")
        print(f"\tKendall: {_corr(scipy.stats.kendalltau, avg_score, tourn)}")

        print("Score vs Time")
        _times = [d.avg_time for d in data]
        print(f"\tSpearman: {_corr(scipy.stats.spearmanr, avg_score, _times)}")
        print(f"\tKendall: {_corr(scipy.stats.kendalltau, avg_score, _times)}")

        print("Score vs Gain")
        print(f"\tSpearman: {_corr(scipy.stats.spearmanr, avg_score, score_time)}")
        print(f"\tKendall: {_corr(scipy.stats.kendalltau, avg_score, score_time)}")
        print("\n\n")
    return tabulate(_data, headers=headers, showindex=True)


################################################################################
##  Simulations
################################################################################

def run_loop(cls, seed):
    agent = cls()
    game = Mathematico(seed=seed)
    game.add_player(agent)

    start_time = time.time()
    scores = game.play(verbose=False)
    end_time = time.time()

    result = scores[0]
    return (seed, result, end_time - start_time)


def run_loop_star(args):
    return run_loop(*args)


################################################################################
##  CLI
################################################################################

def make_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("--file",
        type=str,
        help="The path of the module to import the class from"
    )
    parser.add_argument("--cls",
        type=str,
        help="The name of the class to import from the specified module"
    )
    parser.add_argument("--desc", "-d",
        type=str,
        help="Description of the run"
    )

    parser.add_argument("--no-parallel",
        action="store_true",
        default=False,
        help="Don't use parallel evaluation (e.g. when `input()` is used)."
    )

    parser.add_argument("--verbose", "-v",
        action="store_true",
        default=False,
        help="verbose"
    )

    parser.add_argument("--statistics",
        action="store_true",
        default=False,
        help="Print correlations"
    )

    parser.add_argument("--db-file",
        type=str,
        metavar="PATH",
        default="data.csv",
        help="Which file to load and store to"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--sort-by-score',
        default=False, action='store_true', help='sort by  average score')
    group.add_argument('--sort-by-time-score',
        default=False, action='store_true', help='sort by average score per second')
    group.add_argument('--sort-by-tournament',
        default=True, action='store_true', help='sort by tournament score (default)')

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    verbose = args.verbose

    global DB_FILE
    DB_FILE = args.db_file

    if args.file and args.cls:
        if verbose:
            print("[info] Starting the evaluation")

        # Add the parent directory to the Python path
        parent_dir = os.path.abspath(os.path.dirname(args.file))
        sys.path.append(parent_dir)

        # Load the class from the file path
        module_name = args.file.rstrip("/").replace("\\", "/").split("/")[-1].removesuffix(".py")
        module = importlib.import_module(module_name)
        cls = getattr(module, args.cls)

        # prepare multiprocessing stuff
        results = {}
        times = {}
        if args.no_parallel:
            for seed in tqdm(SEEDS, total=len(SEEDS)):
                seed, result, time_taken = run_loop(cls, seed)
                results[seed] = result
                times[seed] = time_taken
        else:
            # go parallel
            proc = max(1, multiprocessing.cpu_count() - 1)
            if verbose:
                print(f"[info] Using {proc} processes")

            with multiprocessing.Pool(processes=proc) as pool:
                # Run the simulations
                arguments = zip(repeat(cls), SEEDS)
                # there is no istarmap - we will use a run_loop_star that takes one
                # argument and unpacks it for run_loop
                for res in tqdm(pool.imap_unordered(run_loop_star, arguments, chunksize=1), total=len(SEEDS)):
                    seed, result, time_taken = res
                    results[seed] = result
                    times[seed] = time_taken

        # store the data
        scores = [results[s] for s in SEEDS]
        avg_time = statistics.mean(times.values())
        record = Record(args.cls, args.file, args.desc or "", scores, avg_time)
        _store_data(record)

    all_data = _load_data()
    if args.sort_by_score:
        sort = Ranking.BY_SCORE
    elif args.sort_by_time_score:
        sort = Ranking.BY_SCORE_PER_TIME
    elif args.sort_by_tournament:
        sort = Ranking.BY_TOURNAMENT
    else:
        assert False

    print(_prep_data(all_data, sort, args.statistics))



if __name__ == "__main__":
    main()
