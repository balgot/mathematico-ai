from perft import SEEDS
import argparse
from human_player import PyGamePlayer
import time
from mathematico import Mathematico


def main():
    parser = argparse.ArgumentParser(description="Playing one game manually...")
    parser.add_argument("--game",
        type=int,
        required=True,
        help=f"Which game to play, in range [1, {len(SEEDS)}]"
    )

    args = parser.parse_args()

    if args.game < 1 or args.game > len(SEEDS):
        raise ValueError("Invalid argument for game, rerun with --help for details")

    seed = SEEDS[args.game - 1]
    player = PyGamePlayer()
    game = Mathematico(seed=seed)
    game.add_player(player)

    start = time.time()
    score = game.play()[0]
    duration = time.time() - start

    print(f"\nGame: {args.game}\nAchieved score: {score}\nTime [s]: {duration}")
    print("\nMake sure to store the result in the appropriate column"
          "in `data.csv` (first column is game=1) for further evaluation.")


if __name__ == "__main__":
    main()
