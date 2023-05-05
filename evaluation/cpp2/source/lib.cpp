#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>

#include "mcts.hpp"
#include "mcts.hpp"
#include "misc.hpp"
#include "states.hpp"
#include "actions.hpp"
#include "strategy.hpp"
#include "playout.hpp"
#include "scoring.hpp"
#include "graphviz.hpp"

#include <tuple>


inline std::tuple<Position, unsigned int>
mcts_go(const Board &board, Card current_card, int max_time_ms) {
    const auto [d, cards] = find_deck(board);
    MState root(board, d, 25-cards);
    root.card_to_play = current_card;

    MBack back;
    MTermination term;
    MScoring sc;
    MCTS<MState, MAction, MStrat, MPlayout> mcts(root, &back, &term, &sc);

    mcts.setTime(max_time_ms);
    auto a = mcts.calculateAction();
    auto iters = mcts.getIterations();
    return { {a.row, a.col}, iters };
}


PYBIND11_MODULE(_cpp_mcts, m) {
    // module docstring
    m.doc() = "Monte Carlo Tree Search for the game Mathematico, implemented in C++";

    // exported functions
    m.def("mcts", &mcts_go, "Run one iteration of the Monte Carlo Tree Search");
}
