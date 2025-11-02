import math
from typing import List

from data_schema import Instance, Item, Solution
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver


class MultiKnapsackSolver:
    """
    This class can be used to solve the Multi-Knapsack problem
    (also the standard knapsack problem, if only one capacity is used).

    Attributes:
    - instance (Instance): The multi-knapsack instance
        - items (List[Item]): a list of Item objects representing the items to be packed.
        - capacities (List[int]): a list of integers representing the capacities of the knapsacks.
    - model (CpModel): a CpModel object representing the constraint programming model.
    - solver (CpSolver): a CpSolver object representing the constraint programming solver.
    """

    def __init__(self, instance: Instance, activate_toxic: bool = False):
        """
        Initialize the solver with the given Multi-Knapsack instance.

        Args:
        - instance (Instance): an Instance object representing the Multi-Knapsack instance.
        """
        self.items = instance.items
        self.activate_toxic = activate_toxic
        self.capacities = instance.capacities
        self.model = CpModel()
        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True
        # TODO: Implement me!
        # Variables --> one per item, connected to the truck
        truck_set = range(len(self.capacities))
        item_set = range(len(self.items))
        self.vars = {}
        for item in item_set:
            for truck in truck_set:
                self.vars[item, truck] = self.model.new_bool_var(f"x_{item},{truck}")

        # Constraints
        for truck in truck_set:
            self.model.Add(sum(self.items[item].weight*self.vars[item, truck] for item in item_set) <= self.capacities[truck])
        for item in item_set:
            self.model.Add(sum(self.vars[item, truck] for truck in truck_set) <= 1)

        # toxic behavior
        if self.activate_toxic == True:
            self.vars_toxic = {}
            for truck in truck_set:
                self.vars_toxic[truck] = self.model.new_bool_var("toxic Truck")
            for truck in truck_set:
                for item in item_set:
                    # toxic case --> pack item leads to toxic truck --> 1 <= 1
                    if self.items[item].toxic == True:
                        self.model.Add(self.vars[item, truck] <= self.vars_toxic[truck])
                    # non toxic case --> pack item leads to non toxic truck --> 1 <= 1-0 = 1
                    else:
                        self.model.Add(self.vars[item, truck] <= 1 - self.vars_toxic[truck])

        # Objective function
        self.model.maximize(sum(self.items[item].value*self.vars[item, truck] for item in item_set for truck in truck_set))



    def solve(self, timelimit: float = math.inf) -> Solution:
        """
        Solve the Multi-Knapsack instance with the given time limit.

        Args:
        - timelimit (float): time limit in seconds for the cp-sat solver.

        Returns:
        - Solution: a list of lists of Item objects representing the items packed in each knapsack
        """
        # handle given time limit
        if timelimit <= 0.0:
            return Solution(trucks=[])  # empty solution
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit
        # TODO: Implement me!
        status = self.solver.solve(self.model)
        if status in (OPTIMAL, FEASIBLE):
            # create one empty list per truck
            packed = [[] for pack in range(len(self.capacities))]
            for item in range(len(self.items)):
                for truck in range(len(self.capacities)):
                    if self.solver.value(self.vars[item, truck]) == 1:
                        packed[truck].append(self.items[item])
                        break  # item is at least in one truck
            return Solution(trucks = packed)
        else:
            # no solution found --> return empty solution
            return Solution(trucks=[])
