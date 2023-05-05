#pragma once

#include "actions.hpp"
#include "states.hpp"
#include "mcts.hpp"


class MStrat : public ExpansionStrategy<MState, MAction> {
    const bool do_actions;
    int next_idx_card = 0;  // start searching from 1
    int next_row = 0;
    int next_col = -1;

    void find_next_card() {
        for (int i=next_idx_card+1; i<int(state->deck.size()); ++i) {
            if (state->deck[i] > 0) {
                next_idx_card = i;
                return;
            }
        }
        next_idx_card = -1;
    }

    void find_next_position() {
        int position = BOARD_SIZE * next_row + next_col + 1;
        int start_row = position / BOARD_SIZE;
        int start_col = position % BOARD_SIZE;

        for (next_row=start_row; next_row<BOARD_SIZE; ++next_row) {
            for (next_col=start_col; next_col<BOARD_SIZE; ++next_col) {
                if (state->board[next_row][next_col] == 0) {
                    return;
                }
            }
        }

        next_row = -1;
    }

    void find_next_action() {
        if (do_actions) find_next_card();
        else find_next_position();
    }

public:
    MStrat(MState* state) : ExpansionStrategy(state), do_actions(state->card_to_play == NO_CARD) {
        find_next_action();
    }

    virtual MAction generateNext() {
        assert(canGenerateNext());
        auto action = do_actions ? MAction(next_idx_card) : MAction(next_row, next_col);
        find_next_action();
        return action;
    }

    virtual bool canGenerateNext() const {
        return do_actions ? next_idx_card > 0 : (next_col >= 0 && next_row >= 0);
    }
};
