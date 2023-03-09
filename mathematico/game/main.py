from mathematico.game import Arena
from mathematico import Player, HumanPlayer, RandomPlayer, SimulationPlayer, MctsPlayer

if __name__ == "__main__":
    player = MctsPlayer()
    arena = Arena()
    arena.add_player(player)
    
    N_ROUNDS = 1
    scores = arena.run(seed=0, rounds=N_ROUNDS)
    data = {}
    print(data)