'''
Constructive heuristics that returns preferably **feasible** solutions.

@author: Vassilissa Lehoux
'''
from typing import Dict
import random

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.optim.heuristics import Heuristic
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA
import os


class Greedy(Heuristic):
    '''
    A deterministic greedy method to return a solution.
    '''

    def __init__(self, params: Dict=dict()):
        '''
        Constructor
        @param params: The parameters of your heuristic method if any as a
               dictionary. Implementation should provide default values in the function.
        '''
        pass

    def run(self, instance: Instance, params: Dict=dict()) -> Solution:
        '''
        Computes a solution for the given instance.
        Implementation should provide default values in the function
        (the function will be evaluated with an empty dictionary).

        @param instance: the instance to solve
        @param params: the parameters for the run
        '''
        pass


class NonDeterminist(Heuristic):
    '''
    Heuristic that returns different values for different runs with the same parameters
    (or different values for different seeds and otherwise same parameters)
    '''

    def __init__(self, params: Dict=dict()):
        '''
        Constructor
        @param params: The parameters of your heuristic method if any as a
               dictionary. Implementation should provide default values in the function.
        '''
        raise "Not implemented error"

    def run(self, instance: Instance, params: Dict=dict()) -> Solution:
        '''
        Computes a solution for the given instance.
        Implementation should provide default values in the function
        (the function will be evaluated with an empty dictionary).

        @param instance: the instance to solve
        @param params: the parameters for the run
        '''
        raise "Not implemented error"


if __name__ == "__main__":
    # Example of playing with the heuristics
    inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
    heurGreedy = Greedy(params={'alpha_local': 1.0, 'beta_local': 1.0})
    solGreedy = heurGreedy.run(inst)
    pltGreedy = solGreedy.gantt("tab20")
    solGreedy.to_csv()
    pltGreedy.savefig("ganttGreedy.png")
    heurNonDeterminist = NonDeterminist()
    solNonDeterminist = heurNonDeterminist.run(inst)
    pltNonDeterminist = solNonDeterminist.gantt("tab20")
    pltNonDeterminist.savefig("ganttNonDeterminist.png")
