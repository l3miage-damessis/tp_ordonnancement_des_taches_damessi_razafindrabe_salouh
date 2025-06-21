'''
Machine on which operation are executed.

@author: Vassilissa Lehoux
'''
from typing import List
from src.scheduling.instance.operation import Operation


class Machine(object):
    '''
    Machine class.
    When operations are scheduled on the machine, contains the relative information. 
    '''

    def __init__(self, machine_id: int, set_up_time: int, set_up_energy: int, tear_down_time: int,
                 tear_down_energy:int, min_consumption: int, end_time: int):
        '''
        Constructor
        Machine is stopped at the beginning of the planning and need to
        be started before executing any operation.
        @param end_time: End of the schedule on this machine: the machine must be
          shut down before that time.
        '''
        self._machine_id = machine_id
        self._set_up_time = set_up_time
        self._set_up_energy = set_up_energy
        self._tear_down_time = tear_down_time
        self._tear_down_energy = tear_down_energy
        self._min_consumption = min_consumption
        self._end_time = end_time

        self._scheduled_operations: List[Operation] = []
        self._start_times: List[int] = [] 
        self._stop_times: List[int] = []  
        self._available_time = 0

    def reset(self):
        self._scheduled_operations.clear()
        self._start_times.clear()
        self._stop_times.clear()
        self._available_time = 0

    @property
    def set_up_time(self) -> int:
        return self._set_up_time
    
    @property
    def set_up_energy(self) -> int:
        return self._set_up_energy

    @property
    def tear_down_time(self) -> int:
        return self._tear_down_time
    
    @property
    def tear_down_energy(self) -> int:
        return self._tear_down_energy
    
    @property
    def min_consumption(self) -> int:
        return self._min_consumption

    @property
    def machine_id(self) -> int:
        return self._machine_id

    @property
    def scheduled_operations(self) -> List:
        '''
        Returns the list of the scheduled operations on the machine.
        '''
        return self._scheduled_operations
    
    
    @property
    def available_time(self) -> int:
        """
        Returns the next time at which the machine is available
        after processing its last operation of after its last set up.
        """
        return self._available_time

    def add_operation(self, operation: Operation, start_time: int) -> int:
        '''
        Adds an operation on the machine, at the end of the schedule,
        as soon as possible after time start_time.
        Returns the actual start time.
        '''
        schedule_successfully = operation.schedule_at_min_time(self._machine_id, start_time)
        assert(schedule_successfully == True)
        self._scheduled_operations.append(operation)
        self._available_time = operation.end_time
        return operation.start_time
  
    def start(self, at_time: int):
        """
        Start the machine at time at_time.
        """
        assert(len(self._start_times) == len(self._stop_times)), "Cannot start again a machine that is already running"
        assert(self.available_time <= at_time), "Cannot start machine before it is available."
        self._start_times.append(at_time)
        self._available_time = self._start_times[-1] + self._set_up_time

    def stop(self, at_time):
        """
        Stops the machine at time at_time.
        """
        assert(len(self._start_times) == len(self._stop_times) + 1), "Cannot stop a machine that is not running"
        assert(self.available_time <= at_time), "Cannot stop machine before it is available."
        self._stop_times.append(at_time)
        self._available_time = self._stop_times[-1] + self.tear_down_time
        

    @property
    def working_time(self) -> int:
        '''
        Total time during which the machine is running
        '''
        total_working_time = 0
        for i in range(len(self._stop_times)):
            if i < len(self._start_times):
                total_working_time += self._stop_times[i] - self._start_times[i]

        if len(self._start_times) == len(self._stop_times) + 1:
            # Still running, so consider working until end_time
            total_working_time += self._end_time - self._start_times[-1] 

        return total_working_time

    @property
    def start_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is started
        in increasing order
        """
        return sorted(self._start_times)

    @property
    def stop_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is stopped
        in increasing order
        """
        if len(self._start_times) > len(self._stop_times):
            return sorted(self._stop_times + [self._end_time])
        return sorted(self._stop_times)

    @property
    def total_energy_consumption(self) -> int:
        """
        Total energy consumption of the machine during planning exectution.
        """
        energy = 0

        # Setup and teardown energy
        energy += len(self.start_times) * self._set_up_energy
        energy += len(self.stop_times) * self._tear_down_energy

        # Energy for operations
        for op in self._scheduled_operations:
            energy += op.energy

        # Energy for idle time
        total_processing_time = sum(op.end_time - op.start_time for op in self._scheduled_operations)
        total_setup_time = len(self.start_times) * self._set_up_time
        total_teardown_time = len(self.stop_times) * self._tear_down_time
        idle_time = self.working_time - total_processing_time - total_setup_time - total_teardown_time
        energy += idle_time * self._min_consumption

        return energy

    def __str__(self):
        return f"M{self.machine_id}"

    def __repr__(self):
        return str(self)
