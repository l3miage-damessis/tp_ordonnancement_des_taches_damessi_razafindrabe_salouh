'''
Tests for the Job class

@author: Vassilissa Lehoux
'''
import unittest
# Import MagicMock and PropertyMock to simulate the Operation class
from unittest.mock import MagicMock, PropertyMock
from typing import List

from src.scheduling.instance.job import Job


class TestJob(unittest.TestCase):

    def setUp(self):
        """This method is called before each test."""
        # Create an instance of the class to be tested
        self.job = Job(1)

    def tearDown(self):
        """This method is called after each test."""
        pass
    
    def test_initial_state(self):
        """Tests the state of a Job right after its creation."""
        self.assertEqual(self.job.job_id, 1)
        self.assertEqual(self.job.operation_nb, 0)
        self.assertIsNone(self.job.next_operation)
        self.assertTrue(self.job.planned)
        self.assertEqual(self.job.completion_time, 0)

    def test_add_operations_and_precedence_calls(self):
        """
        Tests that 'add_operation' correctly calls the 
        add_successor and add_predecessor methods on the mocks.
        """
        # Create Mocks to simulate Operation objects
        mock_op1 = MagicMock()
        mock_op2 = MagicMock()
        
        # Add the first operation
        self.job.add_operation(mock_op1)
        
        # At this stage, no linking methods should have been called
        mock_op1.add_successor.assert_not_called()
        mock_op1.add_predecessor.assert_not_called()
        
        # Add the second operation
        self.job.add_operation(mock_op2)
        
        # Check that op1 and op2 were correctly added
        self.assertIn(mock_op1, self.job.operations)
        self.assertIn(mock_op2, self.job.operations)
        # Check that Job correctly linked op1 to op2
        mock_op1.add_successor.assert_called_once_with(mock_op2)
        mock_op2.add_predecessor.assert_called_once_with(mock_op1)
        # Check that there were no other unwanted calls
        mock_op2.add_successor.assert_not_called()

    def testCompletionTime(self):
        """
        Tests 'completion_time' by mocking the 'processing_time' property
        of the operations with PropertyMock.
        """
        mock_op1 = MagicMock()
        mock_op2 = MagicMock()
        
        # Mock the 'processing_time' property on the mocks
        # We attach a PropertyMock to the mock's type (class)
        type(mock_op1).processing_time = PropertyMock(return_value=10)
        type(mock_op2).processing_time = PropertyMock(return_value=5)
        
        self.job.add_operation(mock_op1)
        self.job.add_operation(mock_op2)
        
        # Check that the sum of the mocked 'processing_time' is correct
        self.assertEqual(self.job.completion_time, 15)

    def test_planned_property(self):
        """
        Tests the 'planned' property by configuring the 'assigned' attribute
        on the mocked operations.
        """
        mock_op1 = MagicMock()
        mock_op2 = MagicMock()
        
        # Configure the 'assigned' attribute on the mocks
        mock_op1.assigned = False
        mock_op2.assigned = False
        
        self.job.add_operation(mock_op1)
        self.job.add_operation(mock_op2)

        # Both are False, so planned should be False
        self.assertFalse(self.job.planned)
        
        # Set one to True
        mock_op1.assigned = True
        self.assertFalse(self.job.planned)
        
        # Set the second one to True
        mock_op2.assigned = True
        self.assertTrue(self.job.planned)

    def test_reset_calls(self):
        """
        Tests that the Job's 'reset' method correctly calls the 'reset' method
        of each operation.
        """
        mock_op1 = MagicMock()
        mock_op2 = MagicMock()
        
        self.job.add_operation(mock_op1)
        self.job.add_operation(mock_op2)
        
        # Advance the state so that reset has something to do
        self.job.schedule_operation()
        self.assertEqual(self.job.next_operation, mock_op2)
        
        # Call the method under test
        self.job.reset()
        
        # Verify that reset() was called once on each mock
        mock_op1.reset.assert_called_once()
        mock_op2.reset.assert_called_once()
        
        # Also verify that the internal index has been reset
        self.assertEqual(self.job.next_operation, mock_op1)

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
