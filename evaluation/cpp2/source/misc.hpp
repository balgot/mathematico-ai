#pragma once

#include <array>
#include <cstdint>
#include <vector>


using Card = uint8_t;

const uint8_t BOARD_SIZE = 5;
const uint8_t MAX_CARD = 13;
const Card EMPTY = 0;

using Line = std::array<Card, BOARD_SIZE>;
using Board = std::array<Line, BOARD_SIZE>;
using Deck = std::array<uint8_t, MAX_CARD+1>;
using Reward = int;
using Position = std::pair<uint8_t, uint8_t>;

inline std::vector<Position> possible_moves(const Board& b) {
    std::vector<Position> result;
    for (uint8_t i = 0; i < BOARD_SIZE; ++i) {
        for (uint8_t j = 0; j < BOARD_SIZE; ++j) {
            if (b[i][j] == EMPTY) {
                result.emplace_back(i, j);
            }
        }
    }
    return result;
}


enum class StateType {
    POSITION_SELECTION,
    CARD_SELECTION
};