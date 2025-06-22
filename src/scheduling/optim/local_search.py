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

class FirstNeighborLocalSearch(Heuristic):
    '''
    Vanilla local search will first create a solution,
    then at each step try and improve it by looking at
    solutions in its neighborhood.
    The first solution found that improves over the current solution
    replaces it.
    The algorithm stops when no solution is better than the current solution
    in its neighborhood.
    '''
    def __init__(self, params: Dict = dict()):
        self.params = params

    def run(self, instance: Instance, InitClass, NeighborClass, params: Dict = dict()) -> Solution:
        current_params = {**self.params, **params}
        init_heur = InitClass()
        current_solution = init_heur.run(instance, current_params)

        print("[FirstNeighbor] Initial solution:", current_solution)

        neighborhood = NeighborClass(instance, current_params)

        while True:
            neighbor = neighborhood.first_better_neighbor(current_solution)
            if neighbor.evaluate >= current_solution.evaluate:
                break
            current_solution = neighbor

        print("[FirstNeighbor] Final solution:", current_solution)
        return current_solution


class BestNeighborLocalSearch(Heuristic):
    '''
    Vanilla local search will first create a solution,
    then at each step try and improve it by looking at
    solutions in its neighborhood.
    The best solution found that improves over the current solution
    replaces it.
    The algorithm stops when no solution is better than the current solution
    in its neighborhood.
    '''
    def __init__(self, params: Dict = dict()):
        self.params = params

    def run(self, instance: Instance, InitClass, NeighborClass1, NeighborClass2, params: Dict = dict()) -> Solution:
        current_params = {**self.params, **params}
        init_heur = InitClass()
        current_solution = init_heur.run(instance, current_params)

        print("[BestNeighbor] Initial solution:", current_solution)

        neighborhood1 = NeighborClass1(instance, current_params)
        neighborhood2 = NeighborClass2(instance, current_params)

        while True:
            neighbor1 = neighborhood1.best_neighbor(current_solution)
            neighbor2 = neighborhood2.best_neighbor(current_solution)

            best_neighbor = min([neighbor1, neighbor2], key=lambda s: s.evaluate)

            if best_neighbor.evaluate >= current_solution.evaluate:
                break
            current_solution = best_neighbor

        print("[BestNeighbor] Final solution:", current_solution)
        return current_solution


if __name__ == "__main__":
    from src.scheduling.tests.test_utils import TEST_FOLDER_DATA
    import os

    instance_path = os.path.join(TEST_FOLDER_DATA, "jsp1")
    inst = Instance.from_file(instance_path)

    from src.scheduling.optim.constructive import NonDeterminist
    from src.scheduling.optim.neighborhoods import MyNeighborhood1, MyNeighborhood2

    # --- FirstNeighborLocalSearch ---
    heur1 = FirstNeighborLocalSearch()
    sol1 = heur1.run(inst, NonDeterminist, MyNeighborhood1)

    plt1 = sol1.gantt("tab20")
    if sol1.is_feasible:
        plt1.savefig("gantt_FirstNeighbor_Feasible.png")
    else:
        plt1.savefig("gantt_FirstNeighbor_Infeasible.png")
    print("[FirstNeighbor] Gantt saved to gantt_FirstNeighbor.png")

    # --- BestNeighborLocalSearch ---
    heur2 = BestNeighborLocalSearch()
    sol2 = heur2.run(inst, NonDeterminist, MyNeighborhood1, MyNeighborhood2)

    plt2 = sol2.gantt("tab20")
    if sol2.is_feasible:
        plt1.savefig("gantt_BestNeighbor_Feasible.png")
    else:
        plt1.savefig("gantt_BestNeighbor_Infeasible.png")
    print("[BestNeighbor] Gantt saved to gantt_BestNeighbor.png")
