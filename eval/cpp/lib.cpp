#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>

#include "mcts.hpp"
#include "policy.hpp"


PYBIND11_MODULE(_cpp_mcts, m) {
    // module docstring
    m.doc() = "Monte Carlo Tree Search for the game Mathematico, implemented in C++";

    // exported functions
    m.def("mcts", &mcts, "Run one iteration of the Monte Carlo Tree Search");
    m.def("random_policy", &random_policy, "Random rollout policy for MCTS");
}
