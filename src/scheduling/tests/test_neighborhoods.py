import unittest
import copy
import os

from src.scheduling.instance.instance import Instance
from src.scheduling.optim.constructive import Greedy
from src.scheduling.optim.neighborhoods import MyNeighborhood1, MyNeighborhood2
from src.scheduling.solution import Solution
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA



class TestNeighborhoods(unittest.TestCase):
    def setUp(self):
        self.inst = Instance.from_file(os.path.join(TEST_FOLDER_DATA, "jsp1"))
        self.greedy = Greedy()
        self.initial_solution = self.greedy.run(self.inst)
        self.assertTrue(self.initial_solution.is_feasible)

    def test_my_neighborhood1_best_neighbor(self):
        neighborhood = MyNeighborhood1(self.inst)
        neighbor = neighborhood.best_neighbor(copy.deepcopy(self.initial_solution))
        
        self.assertTrue(neighbor.is_feasible)
        self.assertLessEqual(neighbor.evaluate, self.initial_solution.evaluate)

    def test_my_neighborhood1_first_better_neighbor(self):
        neighborhood = MyNeighborhood1(self.inst)
        neighbor = neighborhood.first_better_neighbor(copy.deepcopy(self.initial_solution))

        self.assertTrue(neighbor.is_feasible)
        self.assertLessEqual(neighbor.evaluate, self.initial_solution.evaluate)

    def test_my_neighborhood2_best_neighbor(self):
        neighborhood = MyNeighborhood2(self.inst)
        neighbor = neighborhood.best_neighbor(copy.deepcopy(self.initial_solution))

        self.assertTrue(neighbor.is_feasible)
        self.assertLessEqual(neighbor.evaluate, self.initial_solution.evaluate)

    def test_my_neighborhood2_first_better_neighbor(self):
        neighborhood = MyNeighborhood2(self.inst)
        neighbor = neighborhood.first_better_neighbor(copy.deepcopy(self.initial_solution))

        self.assertTrue(neighbor.is_feasible)
        self.assertLessEqual(neighbor.evaluate, self.initial_solution.evaluate)

if __name__ == '__main__':
    unittest.main()
