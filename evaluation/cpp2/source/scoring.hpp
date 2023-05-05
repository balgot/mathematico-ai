#pragma once

#include "states.hpp"
#include "mcts.hpp"
#include "misc.hpp"

namespace {
const int DIAGONAL_BONUS = 10;
const int PAIR = 10;
const int TWO_PAIRS = 20;
const int THREE_OF_A_KIND = 40;
const int FOUR_OF_A_KIND = 160;
const int FOUR_ONES = 200;
const int FULL_HOUSE = 80;
const int FULL_HOUSE_1_13 = 100;
const int FLUSH = 50;
const int FLUSH_1_10_11_12_13 = 150;

int eval_line(const Line& line) {
    int different_cards = 0;

    std::array<uint8_t, MAX_CARD + 1> cnt{};
    for (const auto& card : line) {
        different_cards += cnt[card] == 0;
        cnt[card]++;
    }
    cnt[0] = 0;  // allow evaluation of incomplete boards

    switch (different_cards) {
        case 5: {
            if (cnt[1] && cnt[10] && cnt[11] && cnt[12] && cnt[13]) {
                return FLUSH_1_10_11_12_13;
            }

            Card min = 15, max = 0;
            for (const auto& card : line) {
                min = std::min(min, card);
                max = std::max(min, card);
            }
            if (min > 0 && max - min == 5 - 1) {
                return FLUSH;
            }

            return 0;
        }
        case 4:
            return PAIR;
        case 3:
            for (const auto& card : line) {
                if (cnt[card] == 3) {
                    return THREE_OF_A_KIND;
                }
            }
            return TWO_PAIRS;
        case 2:
            for (const auto& card : line) {
                if (cnt[card] == 4) {
                    return card == 1 ? FOUR_ONES : FOUR_OF_A_KIND;
                }
            }

            if (cnt[1] == 3 && cnt[13] == 2) {
                return FULL_HOUSE_1_13;
            }

            return FULL_HOUSE;
        default:
            throw std::invalid_argument("wrong combination of values");
    }
}
};  // namespace

int eval(const Board& b) {
    int score = 0;

    // rows
    for (const auto& row : b) {
        score += eval_line(row);
    }

    // cols
    for (int i = 0; i < BOARD_SIZE; ++i) {
        Line column;
        for (int j = 0; j < BOARD_SIZE; ++j) {
            column[j] = b[j][i];
        }
        score += eval_line(column);
    }

    // main diag
    Line main;
    for (int i = 0; i < BOARD_SIZE; ++i) {
        main[i] = b[i][i];
    }
    score += eval_line(main);

    // anti diagonal
    Line anti;
    for (int i = 0; i < BOARD_SIZE; ++i) {
        anti[i] = b[i][BOARD_SIZE - i - 1];
    }
    score += eval_line(anti);

    return score;
}


template <StateType T>
class MScoring;

template <>
class MScoring <StateType::CARD_SELECTION>
    : public Scoring<MathematicoState <StateType::CARD_SELECTION>> {

    using T = MathematicoState <StateType::CARD_SELECTION>;

public:
    virtual float score(const T&) { assert(false); }
};


template <>
class MScoring <StateType::POSITION_SELECTION>
    : public Scoring<MathematicoState <StateType::POSITION_SELECTION>> {

    using T = MathematicoState <StateType::POSITION_SELECTION>;

public:
    virtual float score(const T& s) { return eval(s.board); }
};
