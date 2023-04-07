"""General MCTS implementation."""
import math
import random
import textwrap
import time
from abc import ABC, abstractmethod
from typing import Callable, Hashable, Sequence, TypeVar, Union


Action = TypeVar("Action", bound=Hashable)
"""Action to take to traverse between MCTS states."""


class TreeNodeI(ABC):
    """MCTS tree node template."""

    def __init__(
            self,
            is_terminal: bool,
            parent: 'TreeNodeI | None' = None
    ) -> None:
        self.parent = parent
        self.is_fully_expanded = self.is_terminal = is_terminal
        self.num_visits = 0
        self.total_reward = 0
        # does not care about children
        # state should be implemented via inheritence

    def pprint(self, indent=0) -> str:
        """Pretty-print this node."""
        score = "" if not self.is_terminal else f"\tScore: {self.get_reward()}"
        return textwrap.indent(
            textwrap.dedent(
                f"""\
                    reward: {self.total_reward}
                    visits: {self.num_visits}
                    terminal: {self.is_terminal}{score}\
                """),
            "\t" * indent
        )

    def __str__(self):
        return self.pprint()

    @abstractmethod
    def get_children(self) -> dict[Action, 'TreeNodeI']:
        """Return labelled children of this node."""

    @abstractmethod
    def get_current_player(self) -> int:
        """Return 1 for maximizing, 0 for random, -1 for minimizing player."""

    @abstractmethod
    def get_possible_actions(self) -> Sequence[Action]:
        """Return the sequeunce (list/tuple) of possible actions."""

    @abstractmethod
    def take_action(self, action: Action) -> 'TreeNodeI':
        """Apply action returning the next state."""

    @abstractmethod
    def get_reward(self) -> Union[float, int]:
        """Reward defined for the terminal states."""

    @abstractmethod
    def expand(self) -> 'TreeNodeI':
        """Expand with yet unexplored action, update self.is_expanded."""

    def uct(self, exploration: float) -> float:
        """Apply UCT to this node, with usage of parent."""
        assert self.parent is not None, "Cannot calculate UCT for the root."
        _val = self.get_current_player() * self.total_reward / self.num_visits
        _exp = 2 * math.log(self.parent.num_visits) / self.num_visits
        return _val + exploration * math.sqrt(_exp)

    @abstractmethod
    def best_child(self, exploration: float) -> 'TreeNodeI':
        """Find the best child to explore of this node."""


def random_policy(state: TreeNodeI):
    """
    Use the random rollout policy to simulate the game.

    Traverse the game tree down to a random terminal achievable
    state and return the associated reward.
    """
    while not state.is_terminal:
        available_actions = state.get_possible_actions()  # type: ignore
        if not available_actions:
            raise ValueError(
                f"Non-terminal state has no possible actions: {state}"
            )

        action = random.choice(available_actions)
        state = state.take_action(action)
    return state.get_reward()


class MCTS:
    """Monte-Carlo Tree Search"""

    def __init__(
            self,
            time_limit: 'int | float | None' = None,
            iters_limit: 'int | float | None' = None,
            exploration_const: float = 1 / math.sqrt(2),
            rollout_policy: Callable[[TreeNodeI], float] = random_policy
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
        self.root: 'TreeNodeI | None' = None
        # self.root_: '_TreeNode | None' = None  # the root of the whole tree

    def search(self, from_node: TreeNodeI) -> tuple[Action, float]:
        """
        Find the best move.

        Using MCTS, find the best move starting from the given state.

        Arguments
        =========
            from_node: node to reuse when searching

        Returns
        =======
            best (action-expected reward) pair from the given state

        Contraints
        ==========
            There must be enough time and iterations to perform >=1 round.
            The actions returned are subset of actions at the `from_node`.
        """

        self.root = from_node
        start = time.time()
        end = start + (self.max_time or 0) / 1000

        def is_iter_ok(i):
            return self.max_iters is None or i < self.max_iters

        def is_time_ok(_):
            return self.max_time is None or time.time() < end

        # the loop
        i = 0
        while is_iter_ok(i) and is_time_ok(i):
            self.exec_round()
            i += 1

        # compute the statistics
        children: dict[Action, TreeNodeI] = self.root.get_children()
        actions = list(children.keys())
        exp_values: list[float] = []
        for child in children.values():  # guaranteed same order
            value = child.total_reward / child.num_visits
            exp_values.append(value)

        if len(actions) == 0:
            spent_time = time.time() - start
            max_time = (
                self.max_time / 1000
                if self.max_time is not None
                else "NaN"
            )

            assert False, f"""
                MCTS has not explored any actions. Is this a leaf node or
                are the execution contraints too tight?

                Explored tree:
                    {self.root.pprint()}

                Search statistics:
                    Iterations: {i} / {self.max_iters}
                    Time [s]:   {spent_time} / {max_time}
            """

        # note: this returns always the best action
        return max(zip(actions, exp_values), key=lambda e: e[1])

    def exec_round(self):
        """Do one round of MCTS."""
        before_visits = self.root.num_visits
        node = self.select_node(self.root)
        reward = self.rollout(node)
        self.backpropogate(node, reward)
        assert self.root.num_visits == 1 + before_visits

    def select_node(self, root: TreeNodeI) -> TreeNodeI:
        """Select the next node to expand starting from `root`."""
        node = root
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = node.best_child(self.exploration_const)
            else:
                return node.expand()
        return node

    def backpropogate(self, leaf: TreeNodeI, reward: int):
        """Backpropagete the result of the rollout to the root."""
        node: 'None | TreeNodeI' = leaf
        while node is not None:
            node.num_visits += 1
            assert node.num_visits > 0
            node.total_reward += reward
            node = node.parent
