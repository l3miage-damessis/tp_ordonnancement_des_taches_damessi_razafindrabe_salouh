import unittest
import os
from src.scheduling.instance.instance import Instance
from src.scheduling.optim.local_search import FirstNeighborLocalSearch, BestNeighborLocalSearch
from src.scheduling.optim.constructive import NonDeterminist
from src.scheduling.optim.neighborhoods import MyNeighborhood1, MyNeighborhood2
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA

class TestLocalSearch(unittest.TestCase):
    def setUp(self):
        self.inst = Instance.from_file(os.path.join(TEST_FOLDER_DATA, "jsp1"))

    def test_first_neighbor_local_search(self):
        ls = FirstNeighborLocalSearch()
        sol = ls.run(self.inst, NonDeterminist, MyNeighborhood1)

        self.assertTrue(sol.is_feasible, "La solution FirstNeighbor n'est pas faisable.")
        self.assertLess(sol.evaluate, float('inf'), "L'évaluation ne devrait pas être infinie.")

    def test_best_neighbor_local_search(self):
        ls = BestNeighborLocalSearch()
        sol = ls.run(self.inst, NonDeterminist, MyNeighborhood1, MyNeighborhood2)

        self.assertTrue(sol.is_feasible, "La solution BestNeighbor n'est pas faisable.")
        self.assertLess(sol.evaluate, float('inf'), "L'évaluation ne devrait pas être infinie.")

    def test_best_vs_first_neighbor(self):
        heur1 = FirstNeighborLocalSearch()
        heur2 = BestNeighborLocalSearch()
        sol1 = heur1.run(self.inst, NonDeterminist, MyNeighborhood1)
        sol2 = heur2.run(self.inst, NonDeterminist, MyNeighborhood1, MyNeighborhood2)

        if sol1.is_feasible and sol2.is_feasible:
            self.assertLessEqual(sol2.evaluate, sol1.evaluate,
                "BestNeighbor devrait être au moins aussi bon que FirstNeighbor.")

if __name__ == "__main__":
    unittest.main()
