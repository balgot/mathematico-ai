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

    def __init__(self, state: StateI, parent: '_TreeNode | None' = None):
        self.state = state
        self.is_fully_expanded = self.is_terminal = state.is_terminal()
        self.parent = parent
        self.num_visits = 0
        self.total_reward = 0
        self.children: dict[Action, list[tuple[_TreeNode, float]]] = defaultdict(list)
        """Maps each action to the list of achievable
        states and their probabilities."""

    def add_child(self,
            action: Action,
            state: StateI,
            prob: float
    ) -> '_TreeNode':
        """Add child to the current node."""
        # TODO: does not check the probability distribution
        nodes = self.children[action]
        for node, _ in nodes:
            if node.state == state:
                return node
        new_node = _TreeNode(state, self)
        self.children[action].append((new_node, prob))
        return new_node


    def __str__(self):
        return f"""
            {self.__class__.__name__}:
                reward: {self.total_reward}
                visits: {self.num_visits}
                terminal: {self.is_terminal}
                actions: {self.children.keys()}
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
            for child, p in self.root.children[a]:
                value = child.total_reward / child.num_visits
                expectation += p * value
            exp_values.append(expectation)

        # return stuff
        combined = list(zip(actions, exp_values))
        if not stochastic:
            return [max(combined, key=lambda a,v: v)]
        else:
            return combined

    def exec_round(self):
        """Do one round of MCTS."""
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def selectNode(self, root: _TreeNode):
        """Select the next node to expand starting from `root`."""
        node = root
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.getBestChild(node, self.exploration_const)
            else:
                return self.expand(node)
        return node

    def expand(self, node: _TreeNode):
        """Expand the node."""
        actions = node.state.get_possible_actions()
        for action in actions:
            if action not in node.children:
                newNode = treeNode(node.state.takeAction(action), node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode
        assert False, "Expanding already expanded node"

    def backpropogate(self, node, reward):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = node.state.getCurrentPlayer() * child.totalReward / child.numVisits + explorationValue * math.sqrt(
                2 * math.log(node.numVisits) / child.numVisits)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)
