'''
Tests for the Operation class class

@author: Samuel Damessi
'''
import unittest
from unittest.mock import MagicMock, PropertyMock

from src.scheduling.instance.operation import Operation, OperationScheduleInfo


class TestOperation(unittest.TestCase):

    def setUp(self):
        """This method is called before each test."""
        self.operation = Operation(job_id=1, operation_id=1)
        # Add some default machine options for scheduling tests
        self.operation.add_machine_option(machine_id=1, duration=10, energy=50)
        self.operation.add_machine_option(machine_id=2, duration=15, energy=70)

    def tearDown(self):
        """This method is called after each test."""
        pass

    def test_initial_state(self):
        """Tests the initial state of an Operation object."""
        self.assertEqual(self.operation.job_id, 1)
        self.assertEqual(self.operation.operation_id, 1)
        self.assertEqual(self.operation.predecessors, [])
        self.assertEqual(self.operation.successors, [])
        self.assertIsNone(self.operation._schedule_info)
        self.assertEqual(self.operation._machine_options, {1: (10, 50), 2: (15, 70)})
        self.assertFalse(self.operation.assigned)
        self.assertEqual(self.operation.assigned_to, -1)
        self.assertEqual(self.operation.processing_time, -1)
        self.assertEqual(self.operation.start_time, -1)
        self.assertEqual(self.operation.end_time, -1)
        self.assertEqual(self.operation.energy, -1)
        self.assertEqual(self.operation.min_start_time, 0)

    def test_add_predecessor(self):
        """Tests adding a predecessor operation."""
        pred_op = Operation(job_id=1, operation_id=100)
        
        self.operation.add_predecessor(pred_op)
        
        self.assertIn(pred_op, self.operation.predecessors)
        self.assertIn(self.operation, pred_op.successors) # Check reciprocal call
        self.assertEqual(len(self.operation.predecessors), 1)
        self.assertEqual(len(pred_op.successors), 1)

        # Test adding the same predecessor again (should not duplicate)
        self.operation.add_predecessor(pred_op)
        self.assertEqual(len(self.operation.predecessors), 1)

    def test_add_successor(self):
        """Tests adding a successor operation."""
        succ_op = Operation(job_id=1, operation_id=102)
        
        self.operation.add_successor(succ_op)
        
        self.assertIn(succ_op, self.operation.successors)
        self.assertIn(self.operation, succ_op.predecessors) # Check reciprocal call
        self.assertEqual(len(self.operation.successors), 1)
        self.assertEqual(len(succ_op.predecessors), 1)

        # Test adding the same successor again (should not duplicate)
        self.operation.add_successor(succ_op)
        self.assertEqual(len(self.operation.successors), 1)

    def test_reset(self):
        """Tests the reset method."""
        # Setup a state that can be reset
        self.operation._schedule_info = OperationScheduleInfo(1, 10, 20, 100)
        pred_op = Operation(job_id=1, operation_id=100)
        succ_op = Operation(job_id=1, operation_id=102)
        self.operation.add_predecessor(pred_op)
        self.operation.add_successor(succ_op)

        self.operation.reset()

        self.assertIsNone(self.operation._schedule_info)
        # Note: reset in the provided code clears these, but reciprocal links
        # on other operations are *not* cleared. This test reflects only the operation itself.
        self.assertEqual(self.operation.predecessors, []) 
        self.assertEqual(self.operation.successors, [])

    def test_add_machine_option(self):
        """Tests adding machine options."""
        self.operation.add_machine_option(3, 20, 90)
        self.assertIn(3, self.operation.machine_options)
        self.assertEqual(self.operation.machine_options[3], (20, 90))
        self.assertEqual(len(self.operation.machine_options), 3) # Original 2 + new 1

    def test_is_ready_no_predecessors(self):
        """Tests is_ready when there are no predecessors."""
        self.assertTrue(self.operation.is_ready(at_time=0))
        self.assertTrue(self.operation.is_ready(at_time=100))

    def test_is_ready_with_predecessors(self):
        """Tests is_ready with predecessors, assigned and unassigned."""
        pred_op1 = MagicMock(spec=Operation)
        pred_op2 = MagicMock(spec=Operation)
        
        self.operation.add_predecessor(pred_op1)
        self.operation.add_predecessor(pred_op2)

        # Case 1: Predecessors not assigned
        pred_op1.assigned = False
        pred_op2.assigned = False
        self.assertFalse(self.operation.is_ready(at_time=10))

        # Case 2: One predecessor assigned, one not
        pred_op1.assigned = True
        pred_op1.end_time = 5 # Mock end_time property
        self.assertFalse(self.operation.is_ready(at_time=10))

        # Case 3: Both assigned, but one ends after at_time
        pred_op2.assigned = True
        pred_op1.end_time = 5
        pred_op2.end_time = 15
        self.assertFalse(self.operation.is_ready(at_time=10)) # op2 ends at 15 > 10

        # Case 4: Both assigned and end at or before at_time
        pred_op1.end_time = 5
        pred_op2.end_time = 10
        self.assertTrue(self.operation.is_ready(at_time=10))
        self.assertTrue(self.operation.is_ready(at_time=20))

    def test_min_start_time(self):
        """Tests the min_start_time property."""
        self.assertEqual(self.operation.min_start_time, 0) # No predecessors initially

        pred_op1 = MagicMock(spec=Operation)
        pred_op2 = MagicMock(spec=Operation)
        
        self.operation.add_predecessor(pred_op1)
        self.operation.add_predecessor(pred_op2)

        # Case 1: Predecessors not assigned (min_start_time should still return 0 per implementation)
        pred_op1.assigned = False
        pred_op2.assigned = False
        self.assertEqual(self.operation.min_start_time, 0)

        # Case 2: One assigned
        pred_op1.assigned = True
        type(pred_op1).end_time = PropertyMock(return_value=10)
        self.assertEqual(self.operation.min_start_time, 10) # Max of [10] is 10

        # Case 3: Both assigned, different end times
        pred_op2.assigned = True
        type(pred_op2).end_time = PropertyMock(return_value=25)
        self.assertEqual(self.operation.min_start_time, 25) # Max of [10, 25] is 25

    def test_schedule_success(self):
        """Tests successful scheduling."""
        success = self.operation.schedule(machine_id=1, at_time=0)
        self.assertTrue(success)
        self.assertTrue(self.operation.assigned)
        self.assertEqual(self.operation.assigned_to, 1)
        self.assertEqual(self.operation.start_time, 0)
        self.assertEqual(self.operation.processing_time, 10)
        self.assertEqual(self.operation.end_time, 10)
        self.assertEqual(self.operation.energy, 50)

    def test_schedule_already_assigned(self):
        """Tests scheduling when already assigned."""
        self.operation.schedule(machine_id=1, at_time=0) # First schedule
        success = self.operation.schedule(machine_id=2, at_time=10) # Try to re-schedule
        self.assertFalse(success)
        self.assertEqual(self.operation.assigned_to, 1) # Should remain the first assignment

    def test_schedule_invalid_machine(self):
        """Tests scheduling with an invalid machine ID."""
        success = self.operation.schedule(machine_id=99, at_time=0)
        self.assertFalse(success)
        self.assertFalse(self.operation.assigned)

    def test_schedule_predecessor_not_ready(self):
        """Tests scheduling failure due to predecessors not being ready."""
        pred_op = MagicMock(spec=Operation)
        self.operation.add_predecessor(pred_op)
        pred_op.assigned = False # Not assigned, so not ready
        
        success = self.operation.schedule(machine_id=1, at_time=10, check_success=True)
        self.assertFalse(success)
        self.assertFalse(self.operation.assigned)

    def test_schedule_time_before_min_start_time(self):
        """Tests scheduling failure when requested time is before min_start_time."""
        pred_op = MagicMock(spec=Operation)
        self.operation.add_predecessor(pred_op)
        pred_op.assigned = True
        type(pred_op).end_time = PropertyMock(return_value=20) # Predecessor ends at 20

        # Try to schedule at 10, which is before pred_op's end time
        success = self.operation.schedule(machine_id=1, at_time=10, check_success=True)
        self.assertFalse(success)
        self.assertFalse(self.operation.assigned)

    def test_schedule_without_check_success(self):
        """Tests scheduling when check_success is False (bypasses checks)."""
        pred_op = MagicMock(spec=Operation)
        self.operation.add_predecessor(pred_op)
        pred_op.assigned = False # Normally would fail check_success

        # This should succeed because checks are bypassed
        success = self.operation.schedule(machine_id=1, at_time=10, check_success=False)
        self.assertTrue(success)
        self.assertTrue(self.operation.assigned)
        self.assertEqual(self.operation.start_time, 10)

    def test_schedule_at_min_time_success(self):
        """Tests schedule_at_min_time for successful scheduling."""
        pred_op = MagicMock(spec=Operation)
        self.operation.add_predecessor(pred_op)
        pred_op.assigned = True
        type(pred_op).end_time = PropertyMock(return_value=15) # Predecessor ends at 15

        # Try to schedule at 10, but min_start_time is 15. It should schedule at 15.
        success = self.operation.schedule_at_min_time(machine_id=1, min_time=10)
        self.assertTrue(success)
        self.assertTrue(self.operation.assigned)
        self.assertEqual(self.operation.start_time, 15) # Should be 15, not 10

        # Try to schedule at 20, min_start_time is 15. It should schedule at 20.
        self.operation.reset() # Reset for a new test case
        self.operation.add_predecessor(pred_op) # Re-add predecessor after reset
        success = self.operation.schedule_at_min_time(machine_id=1, min_time=20)
        self.assertTrue(success)
        self.assertTrue(self.operation.assigned)
        self.assertEqual(self.operation.start_time, 20)

    def test_schedule_at_min_time_no_predecessors(self):
        """Tests schedule_at_min_time with no predecessors."""
        success = self.operation.schedule_at_min_time(machine_id=1, min_time=5)
        self.assertTrue(success)
        self.assertEqual(self.operation.start_time, 5)

    def test_schedule_at_min_time_already_assigned(self):
        """Tests schedule_at_min_time when already assigned."""
        self.operation.schedule(machine_id=1, at_time=0)
        success = self.operation.schedule_at_min_time(machine_id=2, min_time=10)
        self.assertFalse(success)
        self.assertEqual(self.operation.assigned_to, 1)

    def test_schedule_at_min_time_invalid_machine(self):
        """Tests schedule_at_min_time with an invalid machine ID."""
        success = self.operation.schedule_at_min_time(machine_id=99, min_time=0)
        self.assertFalse(success)
        self.assertFalse(self.operation.assigned)

    def test_str_unassigned(self):
        """Tests the __str__ representation when the operation is not assigned."""
        expected_str = "O1_J1"
        self.assertEqual(str(self.operation), expected_str)

    def test_str_assigned(self):
        """Tests the __str__ representation when the operation is assigned."""
        # Schedule the operation to set _schedule_info
        self.operation.schedule(machine_id=1, at_time=5)
        # The __str__ method relies on assigned_to, processing_time, energy properties.
        # These properties in turn rely on _schedule_info.machine_id, _schedule_info.duration, _schedule_info.energy_consumption
        # With the values (1, 5, 10, 50) for schedule_info, the properties should be:
        # assigned_to = 1
        # processing_time = 10
        # energy = 50
        expected_str = "O1_J1_M1_ci10_e50"
        self.assertEqual(str(self.operation), expected_str)

    def test_repr(self):
        """Tests that __repr__ calls __str__."""
        # For simplicity, we just check that __repr__ returns the same as __str__.
        # This confirms it uses the __str__ implementation.
        self.assertEqual(repr(self.operation), str(self.operation))
        # Schedule it and check again
        self.operation.schedule(machine_id=1, at_time=5)
        self.assertEqual(repr(self.operation), str(self.operation))


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
