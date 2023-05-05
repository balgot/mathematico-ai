#include "mcts.hpp"
#include "states.hpp"
#include "actions.hpp"
#include <random>

static std::random_device rd;
static std::mt19937 gen(rd());

class MPlayout : public PlayoutStrategy<MState, MAction> {
    std::vector<Position> moves;
    std::discrete_distribution<Card> dist;

public:
    MPlayout(MState* state) : PlayoutStrategy(state) {
        if (state->card_to_play != NO_CARD) {
            moves = possible_moves(state->board);
            dist = { moves.size(), 0, 0, [](auto) { return 1; }};
        }
        else {
            dist = { state->deck.begin(), state->deck.end() };
        }
    }

    virtual void generateRandom(MAction& action) {
        auto res = dist(gen);
        action.c = 0;
        action.row = action.col = -1;

        if (state->card_to_play != NO_CARD) {
            action.row = moves[res].first;
            action.col = moves[res].second;
        }
        else {
            action.c = res;
        }
    }
};
