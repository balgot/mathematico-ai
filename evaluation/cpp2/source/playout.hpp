#include "mcts.hpp"
#include "states.hpp"
#include "actions.hpp"
#include <random>

static std::random_device rd;
static std::mt19937 gen(rd());


template <StateType T>
class MPlayout;


template <>
class MPlayout<StateType::CARD_SELECTION>
    : PlayoutStrategy<MathematicoState<StateType::CARD_SELECTION>, MathematicoAction<StateType::CARD_SELECTION>> {

    using T = MathematicoState<StateType::CARD_SELECTION>;
    using A = MathematicoAction<StateType::CARD_SELECTION>;

    std::discrete_distribution<Card> dist;

public:
    MPlayout(T* state)
        : PlayoutStrategy(state),
          dist(state->deck.begin(), state->deck.end()) {}

    virtual void generateRandom(A& action) {
        auto res = dist(gen);
        action.c = res;
    }
};


template <>
class MPlayout<StateType::POSITION_SELECTION>
    : PlayoutStrategy<MathematicoState<StateType::POSITION_SELECTION>, MathematicoAction<StateType::POSITION_SELECTION>> {

    using T = MathematicoState<StateType::POSITION_SELECTION>;
    using A = MathematicoAction<StateType::POSITION_SELECTION>;


    std::vector<Position> moves;
    std::discrete_distribution<Card> dist;

public:
    MPlayout(T* state) : PlayoutStrategy(state),
        moves(possible_moves(state->board)),
        dist(moves.size(), 0, 0, [](auto) { return 1; })
            {}

    virtual void generateRandom(A& action) {
        auto res = dist(gen);
        action.row = moves[res].first;
        action.col = moves[res].second;
    }
};