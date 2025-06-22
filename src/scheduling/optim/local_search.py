'''
Heuristics that compute an initial solution and 
then improve it.

@author: Vassilissa Lehoux
'''
from typing import Dict

from src.scheduling.optim.heuristics import Heuristic
from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.optim.constructive import Greedy, NonDeterminist
from src.scheduling.optim.neighborhoods import MyNeighborhood1, MyNeighborhood2


# class FirstNeighborLocalSearch(Heuristic):
#     '''
#     Vanilla local search will first create a solution,
#     then at each step try and improve it by looking at
#     solutions in its neighborhood.
#     The first solution found that improves over the current solution
#     replaces it.
#     The algorithm stops when no solution is better than the current solution
#     in its neighborhood.
#     '''

#     def __init__(self, params: Dict=dict()):
#         '''
#         Constructor
#         @param params: The parameters of your heuristic method if any as a
#                dictionary. Implementation should provide default values in the function.
#         '''
#         raise "Not implemented error"

#     def run(self, instance: Instance, InitClass, NeighborClass, params: Dict=dict()) -> Solution:
#         '''
#         Compute a solution for the given instance.
#         Implementation should provide default values in the function
#         (the function will be evaluated with an empty dictionary).

#         @param instance: the instance to solve
#         @param InitClass: the class for the heuristic computing the initialization
#         @param NeighborClass: the class of neighborhood used in the vanilla local search
#         @param params: the parameters for the run
#         '''
#         raise "Not implemented error"


# class BestNeighborLocalSearch(Heuristic):
#     '''
#     Vanilla local search will first create a solution,
#     then at each step try and improve it by looking at
#     solutions in its neighborhood.
#     The best solution found that improves over the current solution
#     replaces it.
#     The algorithm stops when no solution is better than the current solution
#     in its neighborhood.
#     '''

#     def __init__(self, params: Dict=dict()):
#         '''
#         Constructor
#         @param params: The parameters of your heuristic method if any as a
#                dictionary. Implementation should provide default values in the function.
#         '''
#         raise "Not implemented error"

#     def run(self, instance: Instance, InitClass, NeighborClass, params: Dict=dict()) -> Solution:
#         '''
#         Computes a solution for the given instance.
#         Implementation should provide default values in the function
#         (the function will be evaluated with an empty dictionary).

#         @param instance: the instance to solve
#         @param InitClass: the class for the heuristic computing the initialization
#         @param NeighborClass: the class of neighborhood used in the vanilla local search
#         @param params: the parameters for the run
#         '''
#         raise "Not implemented error"


class FirstNeighborLocalSearch(Heuristic):
    def __init__(self, params: Dict = dict()):
        self.params = params

    def run(self, instance: Instance, InitClass, NeighborClass, params: Dict = dict()) -> Solution:
        current_params = {**self.params, **params}
        init_heur = InitClass()
        current_solution = init_heur.run(instance, current_params)
        print("current_solution avant : " +str(current_solution))

        neighborhood = NeighborClass(instance, current_params)

        improved = True
        while improved:
            neighbor_solution = neighborhood.first_better_neighbor(current_solution)
            if neighbor_solution.evaluate >= current_solution.evaluate:
                improved = False
            else:
                current_solution = neighbor_solution
        print("current_solution après : " +str(current_solution))
        return current_solution


class BestNeighborLocalSearch(Heuristic):
    def __init__(self, params: Dict = dict()):
        self.params = params

    def run(self, instance: Instance, InitClass, NeighborClass, params: Dict = dict()) -> Solution:
        current_params = {**self.params, **params}
        init_heur = InitClass()
        current_solution = init_heur.run(instance, current_params)
        print("current_solution avant : " +str(current_solution))
        neighborhood = NeighborClass(instance, current_params)

        improved = True
        while improved:
            neighbor_solution = neighborhood.best_neighbor(current_solution)
            if neighbor_solution.evaluate >= current_solution.evaluate:
                improved = False
            else:
                current_solution = neighbor_solution
        print("current_solution après : " +str(current_solution))
        return current_solution


if __name__ == "__main__":
    # To play with the heuristics
    from src.scheduling.tests.test_utils import TEST_FOLDER_DATA
    import os
    inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
    heur = FirstNeighborLocalSearch()
    sol = heur.run(inst, NonDeterminist, MyNeighborhood2)
    plt = sol.gantt("tab20")
    plt.savefig("ganttNonDeterministLocal.png")
