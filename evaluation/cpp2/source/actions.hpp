#pragma once

#include "states.hpp"
#include "mcts.hpp"
#include "misc.hpp"


class MAction : public Action<MState> {
public:
    int row = -1, col = -1;
    Card c = 0;

    MAction() = default;
    MAction(const MAction&) = default;
    MAction(Card c) : c(c) {}
    MAction(int row, int col) : row(row), col(col) {}

    virtual void execute(MState& state) {
        assert((c > 0) ^ (row > -1 && col > -1));
        if (c > 0) { state.card_to_play = c; }
        else { state.play_move(row, col, state.card_to_play); }
    }

protected:
    virtual void print(std::ostream& strm) {
        strm << "Card: " << int(c) << "\tRow: " << row << " Col: " << col;
    }
};
