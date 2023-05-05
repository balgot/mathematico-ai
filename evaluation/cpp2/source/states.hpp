#pragma once

#include <iomanip>
#include <iostream>
#include <cassert>

#include "mcts.hpp"
#include "misc.hpp"


template <StateType T>
class MathematicoState : public State {
public:
    Board board;
    Deck deck;
    Card card_to_play = -1;

    MathematicoState(Board b, Deck d) : board(b), deck(d) {}

    void play_move(int row, int col, Card c) {
        assert(board[row][col] == 0);
        if (!deck[c]) { std::cout << *this << "\n"; }
        assert(deck[c] > 0);
        assert(0 < c);
        assert(c <= 13);
        board[row][col] = c;
        deck[c]--;
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

        if (card_to_play > 0) {
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


template <StateType T>
class MTermination : public TerminationCheck<MathematicoState<T>> {
public:
    using S = MathematicoState<T>;
    virtual bool isTerminal(const S& state) {
        if constexpr (T == StateType::POSITION_SELECTION) {
            return false;
        }
        else {
            // TODO: improve
            for (int i=0; i<BOARD_SIZE; ++i) {
                for (int j=0; j<BOARD_SIZE; ++j) {
                    if (state.board[i][j] == 0) return false;
                }
            }
            return true;
        }
    }
};

template <StateType T>
class MBack : public Backpropagation<MathematicoState<T>> {
public:
    using S = MathematicoState<T>;

    // TODO: probabs?
    virtual float updateScore(const S& state, float score) { return score; }
};
