"""
Heuristics Module

In branch-and-bound, a relaxation gives an upper bound on the best objective in a branch.
To tighten pruning, you need feasible (integral) solutions to serve as lower bounds.
Instead of waiting for an integral node, you can derive feasible solutions from the relaxation
(e.g., rounding, greedy inclusion) to improve search efficiency.

You can implement heuristics by subclassing `Heuristics` and overriding `search(instance, node)`.
`search` should yield zero or more feasible `RelaxedSolution` objects.
"""

import math
from abc import ABC, abstractmethod
from typing import Tuple

from .instance import Instance
from .relaxed_solution import RelaxedSolution
from .relaxation import MyRelaxationSolver


class HeuristicSolution(RelaxedSolution):
    """
    A feasible heuristic solution.
    Inherits from `RelaxedSolution` for compatibility with the rest of the codebase.
    """

    def copy(self) -> "HeuristicSolution":
        """
        Return a deep copy of this heuristic solution.
        """
        return HeuristicSolution(
            self.instance,
            list(self.selection),
            self.upper_bound,
        )


class Heuristics(ABC):
    """
    Abstract base for heuristic generators.

    Implement `search` to produce feasible solutions from a node's relaxed solution.
    """

    @abstractmethod
    def search(
        self, instance: Instance, relaxed: RelaxedSolution
    ) -> Tuple[HeuristicSolution, ...]:
        """
        Return a tuple of feasible `HeuristicSolution` objects for pruning.
        """
        ...


class MyHeuristic(Heuristics):
    """
    Your heuristic implementation.

    The simplest heuristic returns the node's relaxed solution
    if it is already feasible (integral and within capacity).

    --> here i want to use Greedy_0 for lower bound
    """

    """def search(
        self, instance: Instance, relaxed: RelaxedSolution
    ) -> Tuple[HeuristicSolution, ...]:
        if relaxed.does_obey_capacity_constraint() and relaxed.is_integral():
            heuristic_sol = HeuristicSolution(
                instance, relaxed.selection, relaxed.upper_bound
            )
            return (heuristic_sol,)
        return ()
    """

    best_solution = 0
    best_assignments = []

    def search(
        self, instance: Instance, relaxed: RelaxedSolution
    ) -> Tuple[HeuristicSolution, ...]:
        
        lower_bound, greedy_selection = self.greedy_0(instance, relaxed.selection)

        if relaxed.does_obey_capacity_constraint() and relaxed.is_integral():
            if relaxed.upper_bound > MyHeuristic.best_solution:
                MyHeuristic.best_solution = relaxed.upper_bound
                MyHeuristic.best_assignments = relaxed.selection

        if lower_bound > MyHeuristic.best_solution:
                MyHeuristic.best_solution = lower_bound
                MyHeuristic.best_assignments = greedy_selection

        if MyHeuristic.best_solution >= relaxed.upper_bound:
            return()
        
        heuristic_sol = HeuristicSolution(
            instance, MyHeuristic.best_assignments, MyHeuristic.best_solution
        )
        return (heuristic_sol,)

    # use Greedy_0 to find a lower bound
    def greedy_0(self, instance: Instance, decisions: list) -> tuple:

        print(decisions)
        rankings = MyRelaxationSolver.get_item_order(self, instance)
        assignments = decisions.copy()

        total_value = 0
        current_weight = 0
        
        # chosen items have to be in solution --> pack them completely
        for ratio, value, weight, index in rankings:
            if assignments[index] == 1:
                total_value += value
                current_weight += weight
            # skip not chosen items
            else:
                continue

        # do greedy_0 for all remainig items
        for ratio, value, weight, index in rankings:
            # skip already fixed items
            if (assignments[index] == 1 or assignments[index] == 0):
                continue
            # add complete item, if it fits, else skip item
            if current_weight + weight <= instance.capacity:
                total_value += value
                current_weight += weight
                assignments[index] = 1.0
                print("TOTAL VALUE after packing object", total_value, current_weight, "\n")
            else:
                assignments[index] = 0
        # final total_value can be used as lower bound
        return total_value, assignments