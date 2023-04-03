#include <iostream>
#include "eval.hpp"
#include "mcts.hpp"
#include "misc.hpp"
#include "policy.hpp"


const Board b = {
    Line{ 1, 0, 0, 0, 0 },
    Line{ 1, 2, 0, 0, 0 },
    Line{ 0, 0, 0, 0, 0 },
    Line{ 0, 0, 0, 8, 0 },
    Line{ 4, 0, 0, 0, 0 }
};

const TimePoint MAX_TIME = 50;  // 100ms
const int MAX_SIMULS = 5'000'000;
const float EXP = 1. / std::sqrt(2);

int main() {
    auto [action, reward, simuls, time] = mcts(b, 1, EXP, MAX_SIMULS, MAX_TIME, random_policy);
    std::cout << "MCTS simulation:\n"
        << "\tTime [ms]:   " << time << "\n"
        << "\tSimulations: " << simuls << "\n"
        << "\tReward:      " << reward << "\n"
        << "\tAction:      " << "[" << int(action.first) << ", " << int(action.second) << "]\n";
    return 0;
}

