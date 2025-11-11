"""
Relaxation Module

In branch-and-bound, a relaxation of the original 0/1 knapsack yields an upper bound
on the best feasible solution within a branch. If this bound does not exceed your
current best feasible solution, you can prune that branch and skip exploring it.

This file provides three example strategies:
  1. VeryNaiveRelaxationSolver:
     - Ignores capacity entirely, sets every unfixed item to 1.
     - Fastest, loosest bound.
  2. NaiveRelaxationSolver:
     - Checks that already-fixed items of 1 fit capacity.
     - Sets all unfixed items to 1, ignoring capacity beyond fixed part.
     - Slightly tighter bound than VeryNaive.
  3. MyRelaxationSolver:
     - Stub for your own algorithm (e.g., fractional knapsack, propagation).

You should subclass `RelaxationSolver` and implement `solve(instance, decisions)`
so that:
  a) fixed decisions remain unchanged;
  b) objective >= best 0/1 solution consistent with those decisions.
"""

import abc

from .branching_decisions import BranchingDecisions
from .instance import Instance
from .relaxed_solution import RelaxedSolution


class RelaxationSolver(abc.ABC):
    """
    Abstract base for relaxation strategies.

    Implement `solve` to compute an upper bound on the best 0/1 solution
    consistent with given decisions.
    """

    @abc.abstractmethod
    def solve(
        self, instance: Instance, decisions: BranchingDecisions
    ) -> RelaxedSolution:
        """
        Return a `RelaxedSolution` satisfying:
          - fixed items in `decisions` remain at 0 or 1;
          - upper_bound >= best feasible 0/1 solution under those decisions.
        """
        ...


class VeryNaiveRelaxationSolver(RelaxationSolver):
    """
    A relaxation solver for the knapsack problem that naively sets every unfixed
    item to 1 without considering the capacity constraint. This approach provides
    a very loose upper bound for the problem.

    Explanation:
    The solver assumes that all unfixed items can be fully included in the knapsack
    (i.e., their selection is set to 1.0) regardless of the capacity constraint.
    This results in an overestimation of the objective value, making it an upper
    bound. The rationale is that the true optimal solution cannot exceed this
    value since it must respect the capacity constraint, which this naive approach
    ignores.
    """

    def solve(
        self, instance: Instance, decisions: BranchingDecisions
    ) -> RelaxedSolution:
        # build selection: 1.0 for fixed 1 or unfixed, 0 for fixed 0
        selection = [0.0 if x == 0 else 1.0 for x in decisions]
        # compute objective value
        upper = sum(item.value * sel for item, sel in zip(instance.items, selection))
        return RelaxedSolution(instance, selection, upper)


class NaiveRelaxationSolver(RelaxationSolver):
    """
    Ensure fixed 1's fit capacity; set every unfixed item to 1.
    """

    def solve(
        self, instance: Instance, decisions: BranchingDecisions
    ) -> RelaxedSolution:
        # compute capacity after fixed 1 items
        used = sum(item.weight for item, x in zip(instance.items, decisions) if x == 1)
        if used > instance.capacity:
            return RelaxedSolution.create_infeasible(instance)

        selection = [0.0 if x == 0 else 1.0 for x in decisions]
        upper = sum(item.value * sel for item, sel in zip(instance.items, selection))
        return RelaxedSolution(instance, selection, upper)


class MyRelaxationSolver(RelaxationSolver):
    """
    Your relaxation solver stub.

    Implement any relaxation (e.g., fractional knapsack, propagation) to tighten bounds.

    --> use fractional knapsack:
    upper bound = fractional Knapsack
    lower bound = Greedy 0?
    """
    # returns list with tupels [(ratio, value, weight, index)] sorted by ratio
    def get_item_order(self, instance: Instance) -> list:

        self.instance = instance
        ratios = []
        # calculate ratio value/weight for each item
        for index, item in enumerate(instance.items):
            ratios.append((item.value / item.weight, item.value, item.weight, index))
        
        # sort items by ratio (first entry in tuple) non-increasingly
        ratios.sort(key = lambda x: x[0], reverse=True)
        print(ratios)
        return ratios

    # pack items with decision = 1, use fractional knapsack on remaining items
    # return value and selection
    def fractional_knapsack(self, instance: Instance, decisions: list) -> tuple:

        rankings = self.get_item_order(instance)
        # copy to find selection from fractional knapsack and store also this selection
        assignments = decisions._assignments.copy()

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

        # do fractional knapsack for all remainig items
        for ratio, value, weight, index in rankings:
            # skip already fixed items
            if (assignments[index] == 1 or assignments[index] == 0):
                continue
            # add complete item, if it fits, else add only fitting fraction
            if current_weight + weight <= instance.capacity:
                total_value += value
                current_weight += weight
                assignments[index] = 1.0
            else:
                fraction = (instance.capacity - current_weight) / weight
                total_value += (value * fraction)
                assignments[index] = fraction
                break

        assignments = [0.0 if x is None else x for x in assignments]
        print("TOTAL VALUE end", total_value, current_weight, decisions, assignments, "\n")
        # final total_value can be used as upper bound
        return total_value, assignments
    
    
    """def greedy_0(self, instance: Instance, decisions: list) -> tuple:

        rankings = self.get_item_order(instance)
        assignments = decisions._assignments.copy()

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
"""

    best_solution = 0
    
    def solve(
        self, instance: Instance, decisions: BranchingDecisions
    ) -> RelaxedSolution:
        print(decisions._assignments)
        print("\n")

        used_weight = sum(item.weight for item, x in zip(instance.items, decisions._assignments) if x == 1)
        if used_weight > instance.capacity:
            print("Hello")
            return RelaxedSolution.create_infeasible(instance)
        
        selection = [0.0 if x == 0 else 1.0 for x in decisions._assignments]
        upper_bound, relaxed_selection = self.fractional_knapsack(instance, decisions)
        # greedy_value, greedy_selection = self.greedy_0(instance, decisions)
        #if MyRelaxationSolver.best_solution >= upper_bound:
        #    return RelaxedSolution(instance, selection, MyRelaxationSolver.best_solution)
        print(selection, "\n")
        current_value = sum(item.value * sel for item, sel in zip(instance.items, selection)) # currently relaxed solution
        if current_value > MyRelaxationSolver.best_solution:
            MyRelaxationSolver.best_solution = current_value
        return RelaxedSolution(instance, relaxed_selection, upper_bound)