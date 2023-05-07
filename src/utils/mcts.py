import math
import random
import textwrap
import time
from abc import ABC, abstractmethod
from itertools import count
from typing import Hashable, Sequence, TypeVar, Union, Dict, Tuple, List

Action = TypeVar("Action", bound=Hashable)
"""Action to take to traverse between MCTS states."""


class StateI(ABC):
    def get_cnt(self):
        """
        Return number of occurences this node would have
        in fully expanded card choice states.
        """
        return 1

    @abstractmethod
    def get_current_player(self) -> int:
        """Return 1 for maximizing, 0 for random, -1 for minimizing player."""

    @abstractmethod
    def get_possible_actions(self) -> Sequence[Action]:
        """Return the sequeunce (list/tuple) of possible actions."""

    @abstractmethod
    def take_action(self, action: Action) -> 'StateI':
        """Apply action returning the pnext state."""

    @abstractmethod
    def is_terminal(self) -> bool:
        """Check if the state is terminal."""

    @abstractmethod
    def get_reward(self) -> Union[float, int]:
        """Reward defined for the terminal states."""


def random_policy(state: StateI):
    """
    Use the random rollout policy to simulate the game.

    Traverse the game tree down to a random terminal achievable
    state and return the associated reward.
    """
    while not state.is_terminal():
        available_actions = state.get_possible_actions()
        if not available_actions:
            raise Exception(
                f"Non-terminal state has no possible actions: {state}"
            )

        action = random.choice(available_actions)
        state = state.take_action(action)
    return state.get_reward()


class _TreeNode:
    """MCTS tree node."""

    def __init__(self, state: StateI, parent: '_TreeNode | None' = None):
        self.state = state
        self.is_fully_expanded = self.is_terminal = state.is_terminal()
        self.parent = parent
        self.num_visits = 0
        self.total_reward = 0
        self.children: Dict[Action, _TreeNode] = {}

    def pprint(self, indent=0, action="") -> str:
        _children = '\n'.join(c.pprint(indent + 1, a)
                                for a, c in self.children.items())
        return textwrap.indent(
            textwrap.dedent(
                f"""
                    ({action}) {self.__class__.__name__}:
                        reward: {self.total_reward}
                        visits: {self.num_visits}
                        terminal: {self.is_terminal}
                        actions: {self.children.keys()}

                        {_children}
                """),
            "\t" * indent
        )

    def __str__(self):
        return self.pprint()


class MCTS:
    """Monte-Carlo Tree Search"""

    def __init__(self,
            time_limit: 'int | float | None' = None,
            iters_limit: 'int | float | None' = None,
            exploration_const: float = 1 / math.sqrt(2),
            rollout_policy = random_policy
    ):
        """
        Create the MCTS tree.

        Arguments
        =========
            time_limit: max to to spend searching for the best move
            iters_limit: max iterations to do
            exploration_const: balanced exploration and exploitation
            rollout_policy: how to do rollouts
        """
        if (time_limit is None) and (iters_limit is None):
            raise ValueError(
                "At least one of time_limit and iters_limit must be specified"
            )

        self.exploration_const = exploration_const
        self.rollout = rollout_policy
        self.max_time = time_limit
        self.max_iters = iters_limit
        self.root: '_TreeNode | None' = None
        # self.root_: '_TreeNode | None' = None  # the root of the whole tree

    def search_(self, from_node: _TreeNode) -> Tuple[Action, float]:
        """
        Find the best move.

        Using MCTS, find the best move starting from the given state.

        Arguments
        =========
            from_node: node to reuse when searching

        Returns
        =======
            best (action-expected reward) pair from the given state
        """

        self.root = from_node
        start = time.time()
        end = start + (self.max_time or 0) / 1000

        def is_iter_ok(iter):
            return self.max_iters is None or iter < self.max_iters

        def is_time_ok():
            return self.max_time is None or time.time() < end

        # the loop
        for iter in count():
            if not is_iter_ok(iter) or not is_time_ok():
                break
            self.exec_round()

        # compute the statistics
        actions = list(self.root.children.keys())
        exp_values: List[float] = []
        for a in actions:
            child = self.root.children[a]
            value = child.total_reward / child.num_visits
            exp_values.append(value)

        if len(actions) == 0:
            assert False, f"""
                MCTS has not explored any actions. Is this a leaf node or
                are the execution contraints too tight?

                Explored tree:
                    {self.root.pprint()}

                Current board:
                    {self.root.state.board}

                {iter=} / {self.max_iters}

                time={time.time() - start} / {self.max_time / 1000}
                ({self.max_time=})
            """

        # note: this returns always the best action
        return max(zip(actions, exp_values), key=lambda e: e[1])

    def search(self, state: StateI) -> Tuple[Action, float]:
        """
        Find the best move.

        Using MCTS, find the best move starting from the given state.

        Arguments
        =========
            state: current game state

        Returns
        =======
            best (action-expected reward) pair from the given state
        """
        new_root = _TreeNode(state)
        self.root = new_root
        # self.root_ = new_root
        return self.search_(new_root)

    def exec_round(self):
        """Do one round of MCTS."""
        node = self.select_node(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def select_node(self, root: _TreeNode) -> _TreeNode:
        """Select the next node to expand starting from `root`."""
        node = root
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.best_child(node, self.exploration_const)
            else:
                return self.expand(node)
        return node

    def expand(self, node: _TreeNode) -> _TreeNode:
        """Expand the node."""

        all_actions = list(node.state.get_possible_actions())
        for action in all_actions:
            if action not in node.children:
                new_node = _TreeNode(node.state.take_action(action), node)
                node.children[action] = new_node
                if len(all_actions) == len(node.children):
                    node.is_fully_expanded = True
                return new_node

        assert False, "Expanding already expanded node"

    def backpropogate(self, node: _TreeNode, reward: int):
        """Backpropagete the result of the rollout to the root."""
        while node is not None:
            node.num_visits += 1
            node.total_reward += reward
            node = node.parent

    def _uct(self, node: _TreeNode, exploration: float, parent: _TreeNode) -> float:
        return (
            node.total_reward / node.num_visits +
            exploration * math.sqrt(2 * math.log(parent.num_visits) / (node.num_visits * node.state.get_cnt()))
        )

    def best_child(self, node: _TreeNode, exploration: float) -> _TreeNode:
        """Find the best child of this node based on the UTM formula."""
        best_val = float("-inf")
        best_actions = []

        for action, child in node.children.items():
            value = self._uct(child, exploration, node)

            if value > best_val:
                best_val = value
                best_actions = [action]
            elif value == best_val:
                best_actions.append(action)

        action = random.choice(best_actions)
        return node.children[action]
