from libs.mathematico import Arena
from mcts_player import MctsPlayer

if __name__ == "__main__":
    player = MctsPlayer()
    arena = Arena()
    arena.add_player(player)
    
    N_ROUNDS = 100
    scores = arena.run(seed=0, rounds=N_ROUNDS)
    
    print(sum(scores[0]) / len(scores[0]))