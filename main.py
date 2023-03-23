from libs.mathematico import Arena
from mcts_player import MctsPlayer
from alphamatico_player import AlphamaticoPlayer

if __name__ == "__main__":
    player = MctsPlayer()
    player2 = AlphamaticoPlayer()
    arena = Arena()
    arena.add_player(player)
    arena.add_player(player2)
    
    N_ROUNDS = 1
    scores = arena.run(seed=0, rounds=N_ROUNDS)
    
    print(sum(scores[0]) / len(scores[0]))