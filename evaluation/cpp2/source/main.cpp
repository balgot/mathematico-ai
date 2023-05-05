#include "mcts.hpp"
#include "misc.hpp"
#include "states.hpp"
#include "actions.hpp"
#include "strategy.hpp"
#include "playout.hpp"
#include "scoring.hpp"
#include "graphviz.hpp"
#include <tuple>


const Board b = {
    Line{ 1, 0, 0, 0, 0 },
    Line{ 1, 2, 0, 0, 0 },
    Line{ 0, 0, 0, 0, 0 },
    Line{ 0, 0, 0, 8, 0 },
    Line{ 4, 0, 0, 0, 0 }
};



int main() {
    const auto [d, cards] = find_deck(b);
    MState root(b, d);
    root.card_to_play = 1;
    MBack back;
    MTermination term;
    MScoring sc;
    MCTS<MState, MAction, MStrat, MPlayout> mcts(root, &back, &term, &sc);

    mcts.setTime(1000);
    std::cout << "Starting\n";
    auto a = mcts.calculateAction();
    std::cout << "\nAction: " << a << "\n";
    std::cout << "Iters: " << mcts.getIterations() << "\n";

    return 0;
}