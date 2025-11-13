"""
Branching Strategy Module

Defines how to split (branch) a BnB tree node when its current relaxed solution
is not yet a feasible integer solution. At each branching step:
 1. Select a decision variable that has not been fixed.
 2. Create two children by fixing that variable to 0 (exclude) and 1 (include).
 3. If all variables are fixed, no branches are returned (leaf node).

You should implement your own strategies by subclassing `BranchingStrategy`.
"""

from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from .bnb_nodes import BnBNode, BranchingDecisions


class BranchingStrategy(ABC):
    """
    Abstract base for branching policies based on a node's relaxed solution.

    Subclasses must implement `make_branching_decisions` to return zero,
    two, or more `BranchingDecisions` objects describing child nodes.
    """

    @abstractmethod
    def make_branching_decisions(self, node: BnBNode) -> Iterable[BranchingDecisions]:
        """
        Return an iterable of `BranchingDecisions` to create child nodes.
        If no decisions can be made (all variables fixed), return an empty iterable.
        """
        ...


class FirstUndecidedBranchingStrategy(BranchingStrategy):
    """
    Branch on the first variable that has not yet been fixed.
    """

    def make_branching_decisions(self, node: BnBNode) -> Tuple[BranchingDecisions, ...]:
        # find the smallest index i where no decision has been made
        first_unfixed = min(
            (i for i, val in enumerate(node.branching_decisions) if val is None),
            default=-1,
        )
        if first_unfixed < 0:
            return ()  # leaf node, nothing to branch
        return node.branching_decisions.split_on(first_unfixed)


class MyBranchingStrategy(BranchingStrategy):
    """
    Your implementation of a branching strategy.

    Decide which variable(s) to branch on at each node using information
    from the node's relaxed solution (e.g., fractional values, scores, etc.).
    The simplest strategy is to pick an unfixed variable and split on 0/1.
    """
    
    # branch on the last variable that has not yet been fixed
    def make_branching_decisions(self, node: BnBNode) -> Tuple[BranchingDecisions, ...]:

        last_unfixed = max(
           (i for i, val in enumerate(node.branching_decisions) if val is None),
            default=-1,
        )
        if last_unfixed < 0:
            return ()
        return node.branching_decisions.split_on(last_unfixed)
    

    # branch on best ratio here
    """def make_branching_decisions(self, node: BnBNode) -> Tuple[BranchingDecisions, ...]:
        best_ratio = 0
        best_index = -1 
        for index, val in enumerate(node.branching_decisions):
            if val is None:
                current_value = node.relaxed_solution.instance.items[index].value
                current_weight = node.relaxed_solution.instance.items[index].weight
                current_ratio = current_value / current_weight
                if (current_ratio) > best_ratio:
                    best_ratio = current_ratio
                    best_index = index

        # branch on node with best ratio
        if best_index < 0:
            return ()
        return node.branching_decisions.split_on(best_index)
    """

    # branch on most valuable item
    """def make_branching_decisions(self, node: BnBNode) -> Tuple[BranchingDecisions, ...]:
        highest_value = 0
        best_index = -1 
        for index, val in enumerate(node.branching_decisions):
            if val is None:
                current_value = node.relaxed_solution.instance.items[index].value
                if (current_value) > highest_value:
                    highest_value = current_value
                    best_index = index

        # branch on node with highest value
        if best_index < 0:
            return ()
        return node.branching_decisions.split_on(best_index)
    """

    # branch on item with most weight
    """def make_branching_decisions(self, node: BnBNode) -> Tuple[BranchingDecisions, ...]:
        highest_weight = 0
        best_index = -1 
        for index, val in enumerate(node.branching_decisions):
            if val is None:
                current_weight = node.relaxed_solution.instance.items[index].weight
                if (current_weight) > highest_weight:
                    highest_weight = current_weight
                    best_index = index

        # branch on node with highest weight
        if best_index < 0:
            return ()
        return node.branching_decisions.split_on(best_index)
    """
    
    # branch on item with littlest weight
    """def make_branching_decisions(self, node: BnBNode) -> Tuple[BranchingDecisions, ...]:
        littlest_weight = float("inf")
        best_index = -1
        for index, val in enumerate(node.branching_decisions):
            if val is None:
                current_weight = node.relaxed_solution.instance.items[index].weight
                if (current_weight) <  littlest_weight:
                    littlest_weight = current_weight
                    best_index = index
        # branch on node with littlest weight
        if best_index < 0:
            return ()
        return node.branching_decisions.split_on(best_index)
    """