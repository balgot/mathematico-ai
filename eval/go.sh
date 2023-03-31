for I in `seq 1 3`
do
    python perft.py --file ./random_games.py --cls RandomPlayer --desc "Mathematico Random Player"
    python perft.py --file ./mcts_old/ --cls "MctsPlayer__100_ms" --desc "(pure) [MCTS] 100ms {randomized--old}"
done

# python perft.py --file ./mcts_old/ --cls "MctsPlayer__1s" --desc "(pure) [MCTS] 1 sec {randomized--old}"