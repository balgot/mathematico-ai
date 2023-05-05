#pragma once

#include <iomanip>
#include <iostream>
#include <cassert>

#include "mcts.hpp"
#include "misc.hpp"

Card NO_CARD = 0;

class MState : public State {
public:
    Board board;
    Deck deck;
    Card card_to_play = NO_CARD; // this is set only for states in which the position should be chosen
    int cards_played = 0;

    MState(Board b, Deck d, int cp) : board(b), deck(d), cards_played(cp) {}
    MState(Board b, Deck d) : board(b), deck(d) {
        for (const auto& row : board)
            for (const auto& e: row)
                cards_played += (e != 0);
    }

    void play_move(int row, int col, Card c) {
        assert(board[row][col] == 0);
        assert(deck[c] > 0);
        assert(0 < c);
        assert(c <= 13);
        board[row][col] = c;
        deck[c]--;
        cards_played++;
        card_to_play = NO_CARD;
    }

private:
    void print_pos(std::ostream& strm, Card c) const {
        strm << " " << std::right << std::setw(2) << int(c);
        strm << " ";
    }

    void print_board(std::ostream& strm) const {
        for (const auto& row : board) {
            for (const auto& e: row) {
                print_pos(strm, e);
            }
            strm << "\n";
        }
    }

protected:
    virtual void print(std::ostream& strm) {
        print_board(strm);
        strm << "\n\n";

        if (card_to_play != NO_CARD) {
            strm << "Card: " << int(card_to_play) << "\n";
        }

        strm << "Deck: [";
        for (std::size_t i=0; i<deck.size(); ++i) {
            if (deck[i]) {
                strm << i << " (" << int(deck[i]) << "), ";
            }
        }
        strm << "]\n";
    };
};



class MTermination : public TerminationCheck<MState> {
public:
    virtual bool isTerminal(const MState& state) {
        // final states are those where the last card was places = the ones
        // with full board and no card 2 play
        return state.cards_played == 25; // && state.card_to_play < 0;
    }
};


class MBack : public Backpropagation<MState> {
public:
    // TODO: use probabs?
    virtual float updateScore(const MState& state, float score) {
        (void)state;
        return score;
    }
};
