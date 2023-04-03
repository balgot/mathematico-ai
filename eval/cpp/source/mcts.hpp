#pragma once

#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <functional>
#include <tuple>
#include <unordered_map>

#include "misc.hpp"

/** Action choice for the player - the position to move to. */
using Action = Position;

/** Policy is a function used in rollout phase of MCTS. */
using Policy = std::function<Reward(Board, const Deck &)>;

/** For when there is not action to be done. */
const Action NO_ACTION = {-1, -1};
const Card NO_CARD = -1;

/**
 * @brief MCTS internal tree node
 *
 * Each node represents a relative change to the parent node. The root
 * node has no change. Each time one MCTS phase is run, a temporary board
 * is passed along and incrementally updated.
 *
 * @suggestion: split node into <player node> and <nature node> - this.children.
 */
struct TreeNode {
    //
    // Mathematico related members
    //

    int moves_to_make;  /** How many moves to make on the board. */
    Action action_here; /** Action from the parent that leads here. */
    Card card_here;     /** Card corresponding to `this->action`. */

    //
    // MCTS related members
    //

    TreeNode *parent;                       /** Node's parent, or nullptr of this is the root node. */
    int visits = 0;                         /** Number of visits during MCTS. */
    uint64_t reward = 0;                    /** Accumulated reward in the subtree rooted here. */
    std::vector<TreeNode> children;         /** Children of this node. */
    std::vector<Action> unexplored_actions; /** Actions left to explore. */

    TreeNode(int moves_to_make, Action action_here, Card card_here,
             const Board &b, TreeNode *parent = nullptr)
        : moves_to_make(moves_to_make), action_here(action_here), card_here(card_here), parent(parent), unexplored_actions(possible_moves(b)) {
        // TODO: remove when chaing the ordering of actions
        std::random_shuffle(unexplored_actions.begin(), unexplored_actions.end());
    }

    /** If true, this node is a leaf node. */
    inline bool is_terminal() const { return this->moves_to_make == 0; }

    /** If true, all moves from this node were considered. */
    inline bool is_expanded() const { return this->unexplored_actions.empty(); }
};

namespace MCTS {

/**
 * @brief Selection phase of MCTS.
 *
 * @param parent the root from which subtree we select a leaf
 * @param b edited board (incrementally updated)
 * @param card card to play at the root
 * @param d edited deck (incrementally updated)
 * @param exploration exploration constant for MCTS
 * @return next leaf to run rollout phase from
 */
TreeNode &select(TreeNode &parent, Board &b, Card card, Deck &d, float exploration);

/**
 * @brief Backpropagation phase of MCTS
 *
 * @param r achieved reward
 * @param leaf the leaf node that the rollout originated from
 * @param b edited board (incrementally updated)
 * @param d edited deck (incrementally updated)
 */
void backpropagate(Reward r, TreeNode *leaf, Board &b, Deck &d);

/**
 * @brief Expansion phase of MCTS
 *
 * @param node node to expand
 * @param b edited board (incrementally updated)
 * @param card card to play at the root
 * @param d edited deck (incrementally updated)
 * @return expanded child to examine
 */
TreeNode &expand(TreeNode &node, Board &b, Card card, Deck &d);

/**
 * @brief Do one round of MCTS
 *
 * @param root root of the MCTS tree
 * @param b edited board (incrementally updated)
 * @param card card to place
 * @param d edited deck (incrementally updated)
 * @param p policy for rollout phase
 * @param exploration exploration constant for MCTS
 *
 * @postcondition: `b` and `d` contain the same value as at the beginning
 */
void execute_round(TreeNode &root, Board &b, Card card, Deck &d, const Policy &p, float exploration);

/**
 * @brief Find best child using utb formula.
 *
 * @param parent parent to select a child from
 * @param exploration exploration constant
 * @return best child w.r.t. utb formula
 *
 * @precondition: `parent` has at least one child
 */
TreeNode &find_best_child(TreeNode &parent, float exploration);

}  // namespace MCTS

namespace {
/**
 * @brief Calculate the deck contents
 *
 * @param board current board of Mathematico
 * @return pair of Deck and number of cards that must be drawn from
 *  it to fill up the board
 */
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
}  // namespace

/**
 * @brief Perform MCTS from current game state.
 *
 * @param board the board of Mathematico, 0 for empty, 1-13 for cards
 * @param current_card current selected card
 * @param exploration exploration constant
 * @param max_simulations maximum number of simulations
 * @param max_time_ms maximum time, in miliseconds
 * @param policy rollout policy
 * @return best action, expected score, simulations run, time spent
 *
 * TODO: current card is unused!!
 * TODO: parent..
 */
inline std::tuple<Action, float, int, Duration>
mcts(const Board &board, Card current_card, float exploration, int max_simulations, int max_time_ms, const Policy &policy) {
    // start the timer as soon as possible
    const auto start = now();

    // create the state descritpion
    auto [available_cards, moves_to_make] = find_deck(board);
    Board b(board);  // editable copy of the board for simulations
    TreeNode root(moves_to_make, NO_ACTION, NO_CARD, board);

    // start the iterations
    int iters = 0;
    while (iters < max_simulations) {
        // do not test for time very often
        if (iters % 100 == 0 && start + max_time_ms <= now()) {
            break;
        }

        MCTS::execute_round(root, b, current_card, available_cards, policy, exploration);
        iters++;
    }

    assert(iters > 0);  // if this happend we cannot do anything

    // find the best child and collect search statistics
    const TreeNode &best_child = MCTS::find_best_child(root, 0.f);
    const auto best_action = best_child.action_here;
    float reward = static_cast<float>(best_child.reward) / best_child.visits;
    Duration duration = now() - start;
    return {best_action, reward, iters, duration};
}
