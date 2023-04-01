#include "mcts.hpp"


void MCTS::backpropagate(Reward r, TreeNode *leaf, Board &b, Deck &d) {
    auto node = leaf;
    // the root node has no action nor card
    while (node && node->parent) {
        // unmake the move played on the tmp board
        assert(node->action_here != NO_ACTION);
        assert(node->card_here != NO_CARD);
        assert(node->card_here == b[node->action_here.first][node->action_here.second]);
        d[node->card_here]++;
        b[node->action_here.first][node->action_here.second] = 0;

        // MCTS update
        node->visits++;
        node->reward += r;
        node = node->parent;
    }
}

TreeNode &MCTS::expand(TreeNode &node, Board &b, Card c, Deck &d) {
    assert(!node.is_expanded());

    // TODO: dont take random action from the back
    const auto action = node.unexplored_actions.back();
    node.unexplored_actions.pop_back();

    Card card = 0;
    if (node.action_here == NO_ACTION) {
        card = c;
    }
    else {
        // TODO: dont take first available card
        for (Card i = 1; i < d.size(); ++i) {
            if (d[i] > 0) {
                card = i;
                break;
            }
        }
    }

    // play the move on the tmp board
    assert(card != 0);
    assert(b[action.first][action.second] == 0);
    b[action.first][action.second] = card;
    assert(d[card] > 0);
    d[card]--;

    // add the child
    return node.children.emplace_back(node.moves_to_make - 1, action, card, b, &node);
}

void MCTS::execute_round(TreeNode &root, Board &b, Card card, Deck &d, const Policy &p, float exploration) {

#ifdef DEBUG
    Board entry_board = b;
    Deck entry_deck = d;
#endif // DEBUG

    auto node = MCTS::select(root, b, card, d, exploration);
    auto reward = p(b, d);
    MCTS::backpropagate(reward, &node, b, d);

#ifdef DEBUG
    assert(entry_board == b);
    assert(entry_deck == d);
#endif // DEBUG
};

TreeNode &MCTS::find_best_child(TreeNode &parent, float exploration) {
    assert(parent.children.size());

    float best_value = -1;
    std::size_t best_index = -1;
    for (std::size_t i = 0; i < parent.children.size(); ++i) {
        const auto &child = parent.children[i];
        auto visits = static_cast<float>(child.visits + 1);  // TODO: why we need this?
        assert(visits != 0);

        float child_val = child.reward / visits + exploration * std::sqrt(2 * std::log(parent.visits + 1) / visits);
        assert(child_val >= 0);
        if (child_val > best_value) {
            best_value = child_val;
            best_index = i;
        }
    }

    assert(best_index < parent.children.size());
    return parent.children[best_index];
}

TreeNode &MCTS::select(TreeNode &parent, Board &b, Card card, Deck &d, float exploration) {
    TreeNode *node = &parent;
    assert(parent.action_here == NO_ACTION);

    while (!node->is_terminal()) {
        if (!node->is_expanded()) {
            return MCTS::expand(*node, b, card, d);
        }

        node = &MCTS::find_best_child(*node, exploration);
        assert(node->action_here != NO_ACTION);
        assert(b[node->action_here.first][node->action_here.second] == 0);
        b[node->action_here.first][node->action_here.second] = node->card_here;
        assert(node->card_here > 0);
        assert(node->card_here <= 13);
        assert(d[node->card_here] > 0);
        d[node->card_here]--;
    }

    // at this point, the board and deck are updated for the view from node
    return *node;
};
