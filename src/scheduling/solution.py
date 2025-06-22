'''
Object containing the solution to the optimization problem.

@author: Vassilissa Lehoux
'''
import csv
import os
from typing import List, Tuple
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from src.scheduling.instance.instance import Instance
from src.scheduling.instance.operation import Operation

from matplotlib import colormaps
from src.scheduling.instance.machine import Machine


class Solution(object):
    '''
    Solution class
    '''

    def __init__(self, instance: Instance, alpha: float = 0.5, beta: float = 0.5):
        '''
        Constructor
        '''
        self._instance = instance
        self._alpha = alpha
        self._beta = beta
        self.reset()


    @property
    def inst(self):
        '''
        Returns the associated instance
        '''
        return self._instance


    def reset(self):
        '''
        Resets the solution: everything needs to be replanned
        '''
        for machine in self._instance.machines:
            machine.reset()
        
        for job in self._instance.jobs:
            job.reset()
        
        for operation in self._instance.operations:
            operation.reset()

    @property
    def is_feasible(self) -> bool:
        '''
        Returns True if the solution satisfies all constraints.
        All operations must be scheduled before checking.
        '''
        # 0. All operations must be assigned
        for op in self.all_operations:
            if not op.assigned:
                print(f"Constraint violated: Operation {op.operation_id} is not assigned.")
                return False

        # 1. Machine compatibility: assigned machine must be valid for the operation
        for op in self.all_operations:
            if op.assigned_to not in op.machine_options:
                print(f"Constraint violated: Operation {op.operation_id} assigned to incompatible machine {op.assigned_to}.")
                return False

        # 2. Precedence: predecessors must finish before the operation starts
        for job in self.inst.jobs:
            for op in job.operations:
                for pred_op in op.predecessors:
                    if not pred_op.assigned:
                        print(f"Constraint violated: Predecessor {pred_op.operation_id} of operation {op.operation_id} is not assigned.")
                        return False
                    if op.start_time < pred_op.end_time:
                        print(f"Constraint violated: Operation {op.operation_id} starts before its predecessor {pred_op.operation_id} ends.")
                        return False

        # 3. No overlap: operations on the same machine must not overlap
        for machine in self.inst.machines:
            scheduled_ops = sorted(machine.scheduled_operations, key=lambda op: op.start_time)
            for i in range(len(scheduled_ops) - 1):
                if scheduled_ops[i].end_time > scheduled_ops[i + 1].start_time:
                    print(f"Constraint violated: Operations {scheduled_ops[i].operation_id} and {scheduled_ops[i + 1].operation_id} overlap on machine {machine.machine_id}.")
                    return False

        # 4. Operations must be within active periods of the machine
        for machine in self.inst.machines:
            active_intervals: List[Tuple[int, int]] = []
            for i in range(len(machine.start_times)):
                start = machine.start_times[i] + machine.set_up_time
                end = machine.stop_times[i]
                active_intervals.append((start, end))

            for op in machine.scheduled_operations:
                op_start = op.start_time
                op_end = op.end_time
                if not any(start <= op_start and op_end <= end for start, end in active_intervals):
                    print(f"Constraint violated: Operation {op.operation_id} ({op_start}-{op_end}) not within any active interval on machine {machine.machine_id}.")
                    return False

        # 5. Machine's end time must respect max time constraint
        for machine in self.inst.machines:
            for i in range(len(machine.start_times)):
                b_mk = machine.stop_times[i]
                if b_mk > machine._end_time:
                    print(f"Constraint violated: Machine {machine.machine_id} exceeds max allowed time ({machine._end_time}).")
                    return False

        return True



    @property
    def evaluate(self) -> float:
        '''
        Computes the value of the solution
        '''
        return float('inf') if not self.is_feasible else self.objective

    @property
    def objective(self) -> int:
        '''
        Returns the value of the objective function
        '''
        # E: total energy consumption
        total_energy = self.total_energy_consumption

        # C_max: maximum completion time of a job
        max_completion_time = self.cmax

        return self._alpha * total_energy + self._beta * max_completion_time

    @property
    def cmax(self) -> int:
        '''
        Returns the maximum completion time of a job
        '''
        return max(job.completion_time for job in self._instance.jobs)

    @property
    def sum_ci(self) -> int:
        '''
        Returns the sum of completion times of all the jobs
        '''
        return sum(job.completion_time for job in self._instance.jobs)

    @property
    def total_energy_consumption(self) -> int:
        '''
        Returns the total energy consumption for processing
        all the jobs (including energy for machine switched on but doing nothing).
        '''
        return sum(machine.total_energy_consumption for machine in self._instance.machines)

    def __str__(self) -> str:
        '''
        String representation of the solution
        '''
        if not self.is_feasible:
            return "Solution: Infeasible\n" \
                   f"Cmax: {self.cmax if self.cmax != -1 else 'N/A'}\n" \
                   f"Total Energy: {self.total_energy_consumption}\n" \
                   f"Objective: {self.objective}\n"
        else:
            return f"Solution: Feasible\n" \
                   f"Cmax: {self.cmax}\n" \
                   f"Total Energy: {self.total_energy_consumption}\n" \
                   f"Sum Ci: {self.sum_ci}\n" \
                   f"Objective: {self.objective}\n"

    def to_csv(self, inst_folder="solutions"):
        '''
        Save the solution to a csv files with the following formats:
        Operation file:
          One line per operation
          operation id - machine to which it is assigned - start time
          header: "operation_id,machine_id,start_time"
        Machine file:
          One line per pair of (start time, stop time) for the machine
          header: "machine_id, start_time, stop_time"
        '''
        operation_file = os.path.join(inst_folder, f"{self._instance.name}_operations.csv")
        with open(operation_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["operation_id", "machine_id", "start_time"])
            
            for operation in self._instance.operations:
                if operation.assigned:
                    writer.writerow([operation.operation_id, operation.assigned_to, operation.start_time])
        
        machine_file = os.path.join(inst_folder, f"{self._instance.name}_machines.csv")
        with open(machine_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["machine_id", "start_time", "stop_time"])
            
            for machine in self._instance.machines:
                for start_time, stop_time in zip(machine.start_times, machine.stop_times):
                    writer.writerow([machine.machine_id, start_time, stop_time])


    def from_csv(self, inst_folder, operation_file, machine_file):
        '''
        Reads a solution from the instance folder
        '''
        operation_path = os.path.join(inst_folder, operation_file)
        with open(operation_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                operation_id = int(row['operation_id'])
                machine_id = int(row['machine_id'])
                start_time = int(row['start_time'])
                
                # Trouver l'opération correspondante
                operation = None
                for op in self._instance.operations:
                    if op.operation_id == operation_id:
                        operation = op
                        break
                
                if operation:
                    operation.schedule(machine_id, start_time, check_success=False)
        
        # Lire les informations des machines (si nécessaire pour la reconstruction)
        machine_path = os.path.join(inst_folder, machine_file)
        with open(machine_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                machine_id = int(row['machine_id'])
                start_time = int(row['start_time'])
                stop_time = int(row['stop_time'])
                
                machine = self._instance.get_machine(machine_id)
                if machine:
                    # Reconstruire l'état de la machine
                    machine._start_times.append(start_time)
                    machine._stop_times.append(stop_time)

    @property
    def available_operations(self)-> List[Operation]:
        '''
        Returns the available operations for scheduling:
        all constraints have been met for those operations to start
        '''
        return [op for op in self._instance.operations if not op.assigned and op.is_ready(op.min_start_time)]

    @property
    def all_operations(self) -> List[Operation]:
        '''
        Returns all the operations in the instance
        '''
        return self._instance.operations
    
    def schedule(self, operation: Operation, machine: Machine):
        '''
        Schedules the operation at the end of the planning of the machine.
        Starts the machine if stopped.
        @param operation: an operation that is available for scheduling
        '''
        assert(operation in self.available_operations)
        start_time = max(machine.available_time, operation.min_start_time)
        if not machine.active:
            start_up_time = max(machine.available_time, operation.min_start_time - machine.set_up_time)
            machine.start(start_up_time)
            start_time = max(machine.available_time, start_up_time + machine.set_up_time)
        print("start_time " + str(start_time))
        machine.add_operation(operation, start_time)

    def unschedule(self, op: Operation):
        """
        Fully unschedule the operation: remove from machine and clear schedule info.
        """
        if not op.assigned:
            return

        machine = self.inst.get_machine(op.assigned_to)
        if op in machine.scheduled_operations:
            machine.scheduled_operations.remove(op)

        op.reset()

    def gantt(self, colormapname):
        """
        Generate a plot of the scheduling with operations, setup, teardown, and idle times.
        Standard colormaps can be found at https://matplotlib.org/stable/users/explain/colors/colormaps.html
        """
        fig, ax = plt.subplots()
        colormap = colormaps[colormapname]
        idle_color = '#D3D3D3'
        idle_hatch = '////'

        def draw_block(start, duration, label=None, color=None, hatch=None, fontsize=7, edgecolor='black'):
            ax.broken_barh(
                [(start, duration)],
                (machine.machine_id - 0.4, 0.8),
                facecolors=color,
                edgecolor=edgecolor,
                hatch=hatch,
                linewidth=0.5
            )
            if label:
                ax.text(
                    start + duration / 2,
                    machine.machine_id,
                    label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=fontsize,
                    color='gray' if label == 'idle' else 'black'
                )

        for machine in self.inst.machines:
            operations = sorted(machine.scheduled_operations, key=lambda op: op.start_time)
            set_up_time = machine.set_up_time
            tear_down_time = machine.tear_down_time

            for start, stop in zip(machine.start_times, machine.stop_times):
                setup_end = start + set_up_time
                teardown_start = stop

                # Draw setup and teardown
                draw_block(start, set_up_time, 'set up', colormap(0), None, fontsize=8)
                draw_block(stop, tear_down_time, 'tear down', colormap(1), None, fontsize=8)

                # Get operations within this active window
                ops_in_window = [op for op in operations if setup_end <= op.start_time and op.end_time <= teardown_start]

                # Idle before first operation
                if ops_in_window:
                    if ops_in_window[0].start_time > setup_end:
                        draw_block(setup_end,
                                ops_in_window[0].start_time - setup_end,
                                'idle', idle_color, idle_hatch)

                    # Idle between operations
                    for prev_op, next_op in zip(ops_in_window[:-1], ops_in_window[1:]):
                        if next_op.start_time > prev_op.end_time:
                            draw_block(prev_op.end_time,
                                    next_op.start_time - prev_op.end_time,
                                    'idle', idle_color, idle_hatch)

                    # Idle after last operation
                    if ops_in_window[-1].end_time < teardown_start:
                        draw_block(ops_in_window[-1].end_time,
                                teardown_start - ops_in_window[-1].end_time,
                                'idle', idle_color, idle_hatch)

                    # Draw operations
                    for op in ops_in_window:
                        duration = op.end_time - op.start_time
                        label = f"O{op.operation_id}_J{op.job_id}"
                        color_index = (op.job_id + 2) % colormap.N
                        draw_block(op.start_time, duration, label, colormap(color_index), None, fontsize=8)

        # Axis configuration
        fig.set_size_inches(12, 6)
        ax.set_yticks(range(self._instance.nb_machines))
        ax.set_yticklabels([f'M{mid+1}' for mid in range(self.inst.nb_machines)])
        ax.set_xlabel('Time')
        ax.set_ylabel('Machine')
        ax.set_title('Gantt Chart')
        ax.grid(True)

        # Legend
        legend_elements = [
            Patch(facecolor=colormap(0), edgecolor='black', label='Set up'),
            Patch(facecolor=colormap(1), edgecolor='black', label='Tear down'),
            Patch(facecolor=idle_color, edgecolor='black', hatch=idle_hatch, label='Idle time'),
        ]

        job_ids = sorted({op.job_id for m in self.inst.machines for op in m.scheduled_operations})
        for job_id in job_ids:
            color_index = (job_id + 2) % colormap.N
            legend_elements.append(Patch(facecolor=colormap(color_index), edgecolor='black', label=f'Job {job_id}'))

        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.01, 0.5), title='Legend')
        fig.tight_layout()

        return plt