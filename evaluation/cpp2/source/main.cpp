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


inline std::pair<Deck, int> find_deck(const Board &board) {
    Deck available_cards;
    available_cards.fill(4);
    int moves_to_make = BOARD_SIZE * BOARD_SIZE;
    for (const auto &row : board) {
        for (const auto &e : row) {
            available_cards[e]--;
            moves_to_make -= e != 0;
        }
    }
    available_cards[0] = 0;
    return {available_cards, moves_to_make};
}


#define S  StateType::POSITION_SELECTION
using SS = MathematicoState<S>;
using AA = MathematicoAction<S>;
using Strat = MathematicoStrategy<S>;


int main() {
    const auto [d, cards] = find_deck(b);
    SS root(b, d);
    root.card_to_play = 1;
    MBack<S> back;
    MTermination<S> term;
    MScoring<S> sc;
    MCTS<SS, AA, Strat, MPlayout<S>> mcts(root, &back, &term, &sc);

    try {
        mcts.setTime(100);
        auto a = mcts.calculateAction();
        std::cout << a.row << " " << a.col;
    }
    catch (...) {
        std::cout << root;
    }
}