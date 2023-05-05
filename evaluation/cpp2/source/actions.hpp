#pragma once

#include "states.hpp"
#include "mcts.hpp"
#include "misc.hpp"


template <StateType T>
class MathematicoAction;


template <>
class MathematicoAction<StateType::CARD_SELECTION>
    : public Action<MathematicoState<StateType::CARD_SELECTION>> {

public:

    using S = MathematicoState<StateType::CARD_SELECTION>;
    Card c;

    MathematicoAction() = default;  // idk?
    MathematicoAction(Card c) : c(c) {}
    MathematicoAction(const MathematicoAction&) = default;

    virtual void execute(S& state) {
        state.card_to_play = c;
    }

protected:
    virtual void print(std::ostream& strm) {
        strm << "Card: " << c;
    }
};


template <>
class MathematicoAction<StateType::POSITION_SELECTION>
    : public Action<MathematicoState<StateType::POSITION_SELECTION>> {

public:

    using S = MathematicoState<StateType::POSITION_SELECTION>;
    int row;
    int col;

    MathematicoAction() = default;  // idk?
    MathematicoAction(int row, int col) : row(row), col(col) {}
    MathematicoAction(const MathematicoAction&) = default;

    virtual void execute(S& state) {
        state.play_move(row, col, state.card_to_play);
    }

protected:
    virtual void print(std::ostream& strm) {
        strm << "Position: [" << row << ", " << col << "]";
    }
};
