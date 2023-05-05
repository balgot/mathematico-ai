#pragma once

#include "actions.hpp"
#include "states.hpp"
#include "mcts.hpp"


template <StateType T>
class MathematicoStrategy;


template <>
class MathematicoStrategy<StateType::CARD_SELECTION>
    : public ExpansionStrategy <MathematicoState<StateType::CARD_SELECTION>, MathematicoAction<StateType::CARD_SELECTION>> {

    using A = MathematicoAction<StateType::CARD_SELECTION>;
    using S = MathematicoState<StateType::CARD_SELECTION>;
    int next_idx_action = 0;  // start searching from 1

    void find_next_action() {
        for (int i=next_idx_action+1; i<state->deck.size(); ++i) {
            if (state->deck[i] > 0) {
                next_idx_action = i;
                return;
            }
        }

        next_idx_action = -1;  // no more actions
    }

public:
    MathematicoStrategy(S* state) : ExpansionStrategy(state) {
        find_next_action();
    }

    virtual A generateNext() {
        assert(canGenerateNext());
        auto action = A(next_idx_action);
        find_next_action();
        return action;
    }

    virtual bool canGenerateNext() const { return next_idx_action > 0; }

};


template <>
class MathematicoStrategy<StateType::POSITION_SELECTION>
    : public ExpansionStrategy <MathematicoState<StateType::POSITION_SELECTION>, MathematicoAction<StateType::POSITION_SELECTION>> {

    using A = MathematicoAction<StateType::POSITION_SELECTION>;
    using S = MathematicoState<StateType::POSITION_SELECTION>;

    int next_row = 0;
    int next_col = -1;

    void find_next_action() {
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

public:
    MathematicoStrategy(S* state) : ExpansionStrategy(state) {
        find_next_action();
    }

    virtual A generateNext() {
        assert(canGenerateNext());
        auto action = A(next_row, next_col);
        find_next_action();
        return action;
    }

    virtual bool canGenerateNext() const { return next_col > 0 && next_row > 0; }

};