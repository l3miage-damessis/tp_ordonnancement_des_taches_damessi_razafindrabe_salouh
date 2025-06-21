'''
Tests for the Machine class

@author: Vassilissa Lehoux
'''
import unittest
from unittest.mock import MagicMock, PropertyMock

from src.scheduling.instance.machine import Machine
from src.scheduling.instance.operation import Operation


class TestMachine(unittest.TestCase):
    
    def setUp(self):
        # Common setup for tests, e.g., creating a default machine
        self.machine = Machine(
            machine_id=1,
            set_up_time=10,
            set_up_energy=50,
            tear_down_time=5,
            tear_down_energy=20,
            min_consumption=5,
            end_time=1000
        )

    def tearDown(self):
        # Clean up if necessary
        pass

    def testConstructor(self):
        # Test if the constructor initializes attributes correctly
        self.assertEqual(self.machine.machine_id, 1)
        self.assertEqual(self.machine.set_up_time, 10)
        self.assertEqual(self.machine.set_up_energy, 50)
        self.assertEqual(self.machine.tear_down_time, 5)
        self.assertEqual(self.machine.tear_down_energy, 20)
        self.assertEqual(self.machine.min_consumption, 5)
        self.assertEqual(self.machine._end_time, 1000)
        self.assertEqual(self.machine.available_time, 0)
        self.assertEqual(self.machine.scheduled_operations, [])
        self.assertEqual(self.machine.start_times, [])
        self.assertEqual(self.machine.stop_times, [])

    def testReset(self):
        # Test the reset method
        mock_op = MagicMock(spec=Operation)
        self.machine._scheduled_operations.append(mock_op)
        self.machine._start_times.append(10)
        self.machine._stop_times.append(20)
        self.machine._available_time = 50

        self.machine.reset()
        self.assertEqual(self.machine.scheduled_operations, [])
        self.assertEqual(self.machine.start_times, [])
        self.assertEqual(self.machine.stop_times, [])
        self.assertEqual(self.machine.available_time, 0)

    def testProperties(self):
        # Test all getter properties
        self.assertEqual(self.machine.set_up_time, 10)
        self.assertEqual(self.machine.set_up_energy, 50)
        self.assertEqual(self.machine.tear_down_time, 5)
        self.assertEqual(self.machine.tear_down_energy, 20)
        self.assertEqual(self.machine.min_consumption, 5)
        self.assertEqual(self.machine.machine_id, 1)
        self.assertEqual(self.machine.available_time, 0)
        self.assertEqual(self.machine.scheduled_operations, [])

    def testAddOperation(self):
        # Test add_operation method
        mock_op = MagicMock(spec=Operation)
        
        # Configure the mock operation's behavior
        mock_op.schedule_at_min_time.return_value = True
        type(mock_op).end_time = PropertyMock(return_value=100) # Mock the end_time property
        type(mock_op).start_time = PropertyMock(return_value=50) # Mock the start_time property
        type(mock_op).energy = PropertyMock(return_value=30) # Mock the energy property

        actual_start_time = self.machine.add_operation(mock_op, 0)
        self.assertEqual(actual_start_time, 50)
        self.assertIn(mock_op, self.machine.scheduled_operations)
        self.assertEqual(self.machine.available_time, 100)
        mock_op.schedule_at_min_time.assert_called_with(self.machine.machine_id, 0)

        # Test adding another operation
        mock_op2 = MagicMock(spec=Operation)
        mock_op2.schedule_at_min_time.return_value = True
        type(mock_op2).end_time = PropertyMock(return_value=250)
        type(mock_op2).start_time = PropertyMock(return_value=200)
        type(mock_op2).energy = PropertyMock(return_value=40)

        actual_start_time2 = self.machine.add_operation(mock_op2, 100)
        self.assertEqual(actual_start_time2, 200)
        self.assertIn(mock_op2, self.machine.scheduled_operations)
        self.assertEqual(self.machine.available_time, 250)

    def testStart(self):
        # Test start method
        self.machine.start(at_time=0)
        self.assertEqual(self.machine.start_times, [0])
        self.assertEqual(self.machine.available_time, 0 + self.machine.set_up_time)

        # Test starting again when already running (should assert error)
        with self.assertRaises(AssertionError) as cm:
            self.machine.start(at_time=50)
        self.assertIn("Cannot start again a machine that is already running", str(cm.exception))

    def testStop(self):
        # Test stop method
        self.machine.start(at_time=0)
        self.machine.stop(at_time=100)
        self.assertEqual(self.machine.stop_times, [100])
        self.assertEqual(self.machine.available_time, 100 + self.machine.tear_down_time)

        # Test stopping when not running (should assert error)
        self.machine.reset() # Reset to ensure it's not running
        with self.assertRaises(AssertionError) as cm:
            self.machine.stop(at_time=50)
        self.assertIn("Cannot stop a machine that is not running", str(cm.exception))

    def testWorkingTime(self):
        # Test working_time property
        self.assertEqual(self.machine.working_time, 0)

        # Case 1: Machine started and stopped
        self.machine.start(at_time=0)
        self.machine.stop(at_time=100)
        self.assertEqual(self.machine.working_time, 100)

        # Case 2: Machine started, stopped, started again and stopped
        self.machine.reset()
        self.machine.start(at_time=0)
        self.machine.stop(at_time=50)
        self.machine.start(at_time=60)
        self.machine.stop(at_time=90)
        self.assertEqual(self.machine.working_time, (50 - 0) + (90 - 60)) # 50 + 30 = 80

        # Case 3: Machine started and still running at end_time
        self.machine.reset()
        self.machine.start(at_time=0)
        # Machine still running at self._end_time (1000)
        self.assertEqual(self.machine.working_time, self.machine._end_time - 0) # 1000 - 0 = 1000

        # Case 4: Machine started multiple times, some stopped, last one running
        self.machine.reset()
        self.machine.start(at_time=0)
        self.machine.stop(at_time=50)
        self.machine.start(at_time=60)
        self.machine.stop(at_time=90)
        self.machine.start(at_time=100) # This one is still running
        self.assertEqual(self.machine.working_time, (50 - 0) + (90 - 60) + (self.machine._end_time - 100))
        # 50 + 30 + (1000 - 100) = 80 + 900 = 980

    def testStartAndStopTimesProperties(self):
        
        self.machine.start(at_time=10)
        with self.assertRaises(AssertionError) as cm:
            self.machine.start(at_time=20)
        self.assertIn("Cannot start again a machine that is already running", str(cm.exception))
        self.machine.stop(at_time=20)
        with self.assertRaises(AssertionError) as cm:
            self.machine.stop(at_time=25)
        self.assertIn("Cannot stop a machine that is not running", str(cm.exception))
        
        self.machine.reset()

        self.machine.start(at_time=10)
        self.machine.stop(at_time=30)
        with self.assertRaises(AssertionError) as cm:
            self.machine.start(at_time=20)
        self.assertIn("Cannot start machine before it is available.", str(cm.exception))
        with self.assertRaises(AssertionError) as cm:
            self.machine.stop(at_time=20)
        self.assertIn("Cannot stop a machine that is not running", str(cm.exception))

        self.machine.reset()
        
        self.machine.start(at_time=0)
        self.machine.stop(at_time=50)
        self.machine.start(at_time=60)
        # At this point, machine is running, so end_time should be included in stop_times
        self.assertEqual(self.machine.start_times, [0, 60])
        self.assertEqual(self.machine.stop_times, [50, self.machine._end_time])
        self.machine.stop(at_time=80)
        self.assertEqual(self.machine.stop_times, [50, 80])

    def testTotalEnergyConsumption(self):
        # Test total_energy_consumption property
        # Initial state: no operations, no starts/stops
        self.assertEqual(self.machine.total_energy_consumption, 0)

        # Scenario 1: Machine starts and stops without operations
        self.machine.start(at_time=0)
        self.machine.stop(at_time=100)
        expected_energy = (1 * self.machine.set_up_energy) + \
                          (1 * self.machine.tear_down_energy) + \
                          ((100 - self.machine.set_up_time - self.machine.tear_down_time) * self.machine.min_consumption)
        self.assertEqual(self.machine.total_energy_consumption, expected_energy)
        
        # Scenario 2: Add operations
        self.machine.reset()
        self.machine.start(at_time=0)

        # Mock operations
        mock_op1 = MagicMock(spec=Operation)
        mock_op1.schedule_at_min_time.return_value = True
        type(mock_op1).start_time = PropertyMock(return_value=10)
        type(mock_op1).end_time = PropertyMock(return_value=20) # duration 10
        type(mock_op1).energy = PropertyMock(return_value=70)

        mock_op2 = MagicMock(spec=Operation)
        mock_op2.schedule_at_min_time.return_value = True
        type(mock_op2).start_time = PropertyMock(return_value=30)
        type(mock_op2).end_time = PropertyMock(return_value=45) # duration 15
        type(mock_op2).energy = PropertyMock(return_value=90)

        self.machine.add_operation(mock_op1, 0)
        self.machine.add_operation(mock_op2, 20)
        self.machine.stop(at_time=50)

        # Calculate expected energy
        # Setup energy: 1 start
        expected_energy = self.machine.set_up_energy
        # Teardown energy: 1 stop
        expected_energy += self.machine.tear_down_energy
        # Operation energy
        expected_energy += mock_op1.energy + mock_op2.energy

        # Working time: From start (0) to stop (50) = 50
        # Processing time: (20-10) + (45-30) = 10 + 15 = 25
        # Setup time: 1 * set_up_time = 10
        # Teardown time: 1 * tear_down_time = 5
        # Idle time = Working time - Processing time - Setup time - Teardown time
        # Idle time = 50 - 25 - 10 - 5 = 10
        expected_energy += (10 * self.machine.min_consumption)

        self.assertEqual(self.machine.total_energy_consumption, expected_energy)

        # Scenario 3: Machine running at end_time
        self.machine.reset()
        self.machine.start(at_time=0)
        
        mock_op3 = MagicMock(spec=Operation)
        mock_op3.schedule_at_min_time.return_value = True
        type(mock_op3).start_time = PropertyMock(return_value=10)
        type(mock_op3).end_time = PropertyMock(return_value=20)
        type(mock_op3).energy = PropertyMock(return_value=60)
        self.machine.add_operation(mock_op3, 0)

        # Expected energy when running at end_time
        # Setup energy: 1 * set_up_energy
        expected_energy_running = self.machine.set_up_energy
        # Teardown energy: 1 * tear_down_energy (because stop_times includes end_time)
        expected_energy_running += self.machine.tear_down_energy
        # Operation energy: mock_op3.energy
        expected_energy_running += mock_op3.energy
        
        # Working time: self._end_time - 0 = 1000
        # Processing time: (20 - 10) = 10
        # Setup time: 1 * set_up_time = 10
        # Teardown time: 1 * tear_down_time = 5
        # Idle time = 1000 - 10 - 10 - 5 = 975
        expected_energy_running += (975 * self.machine.min_consumption)
        self.assertEqual(self.machine.total_energy_consumption, expected_energy_running)

    def testStrAndRepr(self):
        # Test __str__ and __repr__ methods
        self.assertEqual(str(self.machine), "M1")
        self.assertEqual(repr(self.machine), "M1")


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
