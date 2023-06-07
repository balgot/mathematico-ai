#!/bin/bash

set -e

help() {
    echo "Running All Comparison of Avaiable Agents"
    echo
    echo "Usage:"
    echo "  bash $0 <path_to_save_data.csv>"
    echo
}

FILE=$1
if [ "$#" -lt 1 ] || [ -f "$FILE" ]; then
    help
    >&2 echo "File $FILE already exists or there are not enough arguments, aborting..."
    exit 1
fi

test_agent() {
    echo "Testing $1/$2#$3"
    python perft.py --file $1 --cls $2 --desc "$2 #$3" --db-file $FILE > /dev/null
}

cp data_human_20.csv $FILE

# testing with 5 random agents
for RANDOM_AGENT in `seq 1 5`; do
    test_agent players/random_player.py RandomPlayer $RANDOM_AGENT
done

# 3 of each mcts (except big ones)
for AGENT in `seq 1 3`; do
    for CLS in 10 20 50 100 250; do
        test_agent players/mcts_player.py MCTS__$CLS $AGENT
        test_agent players/open_spiel_mcts.py OpenSpiel__$CLS $AGENT
    done
done

# one from mcts biggest
test_agent players/mcts_player.py MCTS__500 0
test_agent players/open_spiel_mcts.py OpenSpiel__500 0
test_agent players/open_spiel_mcts.py OpenSpiel__1000 0

python perft.py --db-file $FILE
