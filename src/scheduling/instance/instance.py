'''
Information for the instance of the optimization problem.

@author: Vassilissa Lehoux
'''
from typing import List
import os
import csv

from src.scheduling.instance.job import Job
from src.scheduling.instance.operation import Operation
from src.scheduling.instance.machine import Machine


class Instance(object):
    '''
    classdocs
    '''

    def __init__(self, instance_name):
        '''
        Constructor
        '''
        self._instance_name = instance_name
        self._machines = {}
        self._jobs = {}
        self._operations = {}

    @classmethod
    def from_file(cls, folderpath):
        inst = cls(os.path.basename(folderpath))
        # reading machine info
        with open(folderpath + os.path.sep + inst._instance_name + '_mach.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for row in csv_reader:
                machine_id = int(row[0])
                set_up_time = int(row[1])
                set_up_energy = int(row[2])
                tear_down_time = int(row[3])
                tear_down_energy = int(row[4])
                min_consumption = int(row[5])
                end_time = int(row[6])
                
                inst._machines[machine_id] = Machine(
                    machine_id, set_up_time, set_up_energy,
                    tear_down_time, tear_down_energy,
                    min_consumption, end_time
                )

        # Reading the operation info
        with open(folderpath + os.path.sep + inst._instance_name + '_op.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for row in csv_reader:
                job_id = int(row[0])
                operation_id = int(row[1])
                machine_id = int(row[2])
                processing_time = int(row[3])
                energy_consumption = int(row[4])

                # Get or create Job
                if job_id not in inst._jobs:
                    inst._jobs[job_id] = Job(job_id)

                # Get or create Operation
                op_key = (job_id, operation_id)
                if op_key not in inst._operations:
                    operation = Operation(job_id, operation_id)
                    inst._operations[op_key] = operation
                    inst._jobs[job_id].add_operation(operation)
                else:
                    operation = inst._operations[op_key]

                # Add machine options to this operation
                operation._machine_options[machine_id] = (processing_time, energy_consumption)

        
        return inst

    @property
    def name(self):
        return self._instance_name

    @property
    def machines(self) -> List[Machine]:
        return list(self._machines.values())

    @property
    def jobs(self) -> List[Job]:
        return list(self._jobs.values())

    @property
    def operations(self) -> List[Operation]:
        return list(self._operations.values())

    @property
    def nb_jobs(self):
        return len(self._jobs)

    @property
    def nb_machines(self):
        return len(self._machines)

    @property
    def nb_operations(self):
        return len(self._operations)

    def __str__(self):
        return f"{self.name}_M{self.nb_machines}_J{self.nb_jobs}_O{self.nb_operations}"

    def get_machine(self, machine_id) -> Machine:
        return self._machines[machine_id]

    def get_job(self, job_id) -> Job:
        return self._jobs[job_id]

    def get_operation(self, operation_id) -> Operation:
        return self._operations[operation_id]
