#pragma once

#include <algorithm>
#include <vector>
#include "misc.hpp"
#include "eval.hpp"



int random_policy(Board board, const Deck& deck) {
    std::vector<Card> available_cards;
    available_cards.reserve(4 * 13);
    for (Card i=1; i<deck.size(); ++i) {
        for (std::size_t j=0; j<deck[i]; ++j) {
            available_cards.push_back(i);
        }
    }

    auto available_positions = possible_moves(board);
    std::random_shuffle(available_cards.begin(), available_cards.end());
    std::random_shuffle(available_positions.begin(), available_positions.end());

    for (std::size_t i=0; i<std::min(available_positions.size(), available_cards.size()); ++i) {
        const auto& [row, col] = available_positions[i];
        board[row][col] = available_cards[i];
    }

    return eval(board);
}
