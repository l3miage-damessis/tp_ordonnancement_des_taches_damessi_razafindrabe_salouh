import os
import unittest

from src.scheduling.instance.instance import Instance
from src.scheduling.optim.constructive import Greedy, NonDeterminist
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA


class TestConstructive(unittest.TestCase):

    def setUp(self):
        self.instance = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp3")
        self.instance2 = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp3")

    def tearDown(self):
        pass

    def testGreedy(self):
        heuristic = Greedy()
        first_solution = heuristic.run(self.instance)
        second_solution = heuristic.run(self.instance2)
        self.assertEqual(first_solution.evaluate, second_solution.evaluate, "Les solutions ne sont pas égales")
        self.assertEqual(first_solution.evaluate, 257, "Les solutions ne sont pas égales")
        self.assertTrue(first_solution.is_feasible)

if __name__ == "__main__":
    unittest.main()