#!/bin/bash

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
exit 0

test_agent() {
    echo "Testing $1/$2#$3"
    python perft.py --file $1 --cls $2 --desc "$2 #$3" --db-file $FILE > /dev/null
}

cp data_human_20.csv $FILE

# testing with 5 random agents
for RANDOM_AGENT in `seq 1 5`; do
    test_agent random_player.py RandomPlayer $RANDOM_AGENT
done

# two of each mcts
for AGENT in `seq 1 2`; do
    for CLS in MCTS__100ms MCTS__1s; do  # MCTS__10s ??
        test_agent mcts_player.py $CLS $AGENT
    done
done

python perft.py --db-file $FILE
