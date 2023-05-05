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


enum class StateType {
    POSITION_SELECTION,
    CARD_SELECTION
};