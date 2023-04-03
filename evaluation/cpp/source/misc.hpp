#pragma once

#include <array>
#include <cstdint>
#include <chrono>
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
using TimePoint = std::chrono::milliseconds::rep; // A value in milliseconds


inline TimePoint now() {
    return std::chrono::duration_cast<std::chrono::milliseconds>
        (std::chrono::steady_clock::now().time_since_epoch()).count();
}

using Duration = decltype(now() - now());

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
