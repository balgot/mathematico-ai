import time
import math
import random
from abc import ABC, abstractmethod
from typing import Union, Sequence, TypeVar, Hashable, Literal
from itertools import count
from collections import defaultdict


Action = TypeVar("Action", bound=Hashable)
"""Action to take to traverse between MCTS states."""


class StateI(ABC):
    @abstractmethod
    def get_possible_actions(self) -> Sequence[Action]:
        """Return the sequeunce (list/tuple) of possible actions."""

    @abstractmethod
    def take_action(self, action) -> 'list[tuple[StateI, float]]':
        """
        Apply action returning the probability distribution
        on resulting states.
        """

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
        try:
            action = random.choice(state.get_possible_actions())
        except IndexError as e:
            raise Exception(
                f"Non-terminal state has no possible actions: {state}"
            ) from e
        possible_states = state.take_action(action)
        states = [s for s, p in possible_states]
        probabs = [p for s, p in possible_states]
        state = random.choices(states, probabs, k = 1)[0]
    return state.get_reward()


class _TreeNode:
    """MCTS tree node."""

    def __init__(self, state: StateI, p: float = 1, parent: '_TreeNode | None' = None):
        self.state = state
        self.p = p  # probability getting here
        self.is_fully_expanded = self.is_terminal = state.is_terminal()
        self.parent = parent
        self.num_visits = 0
        self.total_reward = 0
        self.children: dict[Action, list[_TreeNode]] = defaultdict(list)
        """Maps each action to the list of achievable states"""

    def add_child(self,
            action: Action,
            state: StateI,
            prob: float
    ) -> '_TreeNode':
        """Add child to the current node."""
        # TODO: does not check the probability distribution
        nodes = self.children[action]
        for node in nodes:
            if node.state == state:
                return node
        new_node = _TreeNode(state, prob, self)
        self.children[action].append(new_node)
        return new_node


    def __str__(self):
        return f"""
            {self.__class__.__name__}:
                reward: {self.total_reward}
                visits: {self.num_visits}
                terminal: {self.is_terminal}
                actions: {self.children.keys()}
                probab: {self.p}
        """


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

    def search(self,
            state: StateI,
            stochastic: bool = False  # not used yet
    ) -> list[tuple[Action, float]]:
        """
        Find the best move.

        Using MCTS, find the best move starting from the given state.

        Arguments
        =========
            state
            stochastic: if true, returns a list of action-reward
                values, otherwise returns only one such pair

        Returns
        =======
            list of action-expected reward pairs from the given state
        """
        self.root = _TreeNode(state)
        start = time.time()
        end = start + (self.max_time or 0) / 1000

        def is_iter_ok(iter):
            return self.max_iters is None or iter < self.max_iters

        def is_time_ok(iter):
            return self.max_time is None or time.time() < end

        # the loop
        for iter in count():
            if not is_iter_ok(iter) or not is_time_ok(iter):
                break
            self.exec_round()

        # compute the statistics
        actions = list(self.root.children.keys())
        exp_values: list[float] = []
        for a in actions:
            expectation = 0
            for child in self.root.children[a]:
                value = child.total_reward / child.num_visits
                expectation += child.p * value
            exp_values.append(expectation)

        # return stuff
        combined = list(zip(actions, exp_values))
        if not stochastic:
            return [max(combined, key=lambda a,v: v)]
        else:
            return combined

    def exec_round(self):
        """Do one round of MCTS."""
        node = self.select_node(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def select_node(self, root: _TreeNode):
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
        # TODO: decide whether to pursue new action or expand older actions
        # here: find the first unexpanded child

        actions = node.state.get_possible_actions()

        # TODO: this gets repeated often, add a flag somewhere?
        for aidx, action in enumerate(actions):
            children = node.children[action]
            child_states = [c.state for c in children]

            # TODO: break out sooner by checking the length of the lists
            sp = node.state.take_action(action)
            for sidx, (state, p) in enumerate(sp):
                # TODO: costly
                if state not in child_states:
                    children.append(_TreeNode(state, p, node))

                # TODO: check if the node is fully expanded
                # here: assuming deterministic ordering of actions and next states
                if aidx == len(actions) - 1 and sidx == len(sp) - 1:
                    node.is_fully_expanded = True

                return children[-1]

        assert False, "Expanding already expanded node"

    def backpropogate(self, node: _TreeNode, reward: 'float | int'):
        """Backpropagete the result of the rollout to the root."""
        prob = 1
        while node is not None:
            node.num_visits += 1
            node.total_reward += reward * prob
            prob = node
            node = node.parent

    def _utm(self, node: _TreeNode, exploration: float, root_visits: int) -> float:
        return (
            node.total_reward / node.num_visits +
            exploration * math.sqrt(2 * math.log(root_visits) / node.num_visits)
        )

    def best_child(self, node: _TreeNode, exploration: float) -> _TreeNode:
        """Find the best child of this node based on the UTM formula."""
        best_val = float("-inf")
        best_actions = []

        for action, children in node.children.items():
            value = 0
            for child in children:
                _val = self._utm(child, exploration, node.num_visits)
                value += _val * child.p

            if value > best_val:
                best_val = value
                best_actions = [action]
            elif value == best_val:
                best_actions.append(action)

        action = random.choice(action)
        possible_children = node.children[action]
        probabs = [c.p for c in possible_children]
        child = random.choices(possible_children, probabs, k=1)
        return child
