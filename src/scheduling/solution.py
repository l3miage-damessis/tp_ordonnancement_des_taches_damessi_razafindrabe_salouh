'''
Object containing the solution to the optimization problem.

@author: Vassilissa Lehoux
'''
import csv
import os
from typing import List
from matplotlib import pyplot as plt
from src.scheduling.instance.instance import Instance
from src.scheduling.instance.operation import Operation

from matplotlib import colormaps
from src.scheduling.instance.machine import Machine


class Solution(object):
    '''
    Solution class
    '''

    def __init__(self, instance: Instance):
        '''
        Constructor
        '''
        raise "Not implemented error"


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
        raise "Not implemented error"

    @property
    def is_feasible(self) -> bool:
        '''
        Returns True if the solution respects the constraints.
        To call this function, all the operations must be planned.
        '''
        raise "Not implemented error"

    @property
    def evaluate(self) -> int:
        '''
        Computes the value of the solution
        '''
        return int('inf') if not self.is_feasible else self.objective

    @property
    def objective(self) -> int:
        '''
        Returns the value of the objective function
        '''
        raise "Not implemented error"

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
                   f"Total Energy: {self.total_energy_consumption}\n"
        else:
            return f"Solution: Feasible\n" \
                   f"Cmax: {self.cmax}\n" \
                   f"Total Energy: {self.total_energy_consumption}\n" \
                   f"Sum Ci: {self.sum_ci}\n"

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
        raise "Not implemented error"

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
            start_up_time = max(0, operation.min_start_time - machine.set_up_time)
            machine.start(start_up_time)
            start_time = max(machine.available_time, start_up_time + machine.set_up_time)
        machine.add_operation(operation, start_time)

    def gantt(self, colormapname):
        """
        Generate a plot of the planning.
        Standard colormaps can be found at https://matplotlib.org/stable/users/explain/colors/colormaps.html
        """
        fig, ax = plt.subplots()
        colormap = colormaps[colormapname]

        # Define a distinct color for idle time (e.g., light grey)
        idle_color = '#D3D3D3' # Light grey hex code

        for machine in self.inst.machines:
            # Sort all activities for the machine: operations, set-up, and tear-down
            # We'll create temporary "activity" objects to sort them by start time
            all_activities = []

            # Add operations
            for op in machine.scheduled_operations:
                all_activities.append({'type': 'operation', 'start': op.start_time, 'end': op.end_time, 'data': op})

            # Add set-up and tear-down as distinct activities
            for i in range(len(machine.start_times)):
                start_machine_period = machine.start_times[i]
                stop_machine_period = machine.stop_times[i]
                
                # Set-up activity
                set_up_start = start_machine_period
                set_up_end = set_up_start + machine.set_up_time
                all_activities.append({'type': 'setup', 'start': set_up_start, 'end': set_up_end, 'data': None})

                # Tear-down activity
                tear_down_start = stop_machine_period - machine.tear_down_time # Teardown ends at machine stop time
                tear_down_end = stop_machine_period
                all_activities.append({'type': 'teardown', 'start': tear_down_start, 'end': tear_down_end, 'data': None})

            # Sort all activities by their start time
            all_activities.sort(key=lambda x: x['start'])

            # Now, iterate through the distinct machine active periods
            for period_idx in range(len(machine.start_times)):
                machine_period_start = machine.start_times[period_idx]
                machine_period_end = machine.stop_times[period_idx]
                
                # `last_activity_end_time` should start from the beginning of the current machine active period
                last_activity_end_time = machine_period_start

                # Filter activities that fall within the current machine active period
                activities_in_period = [
                    act for act in all_activities 
                    if act['start'] >= machine_period_start and act['end'] <= machine_period_end
                ]
                # Sort these activities again to ensure correct order within the period
                activities_in_period.sort(key=lambda x: x['start'])

                for activity in activities_in_period:
                    activity_start = activity['start']
                    activity_end = activity['end']
                    activity_duration = activity_end - activity_start
                    activity_type = activity['type']

                    # Plot idle time before the current activity if there's a gap
                    # Ensure idle time is within the machine's active period and valid duration
                    if activity_start > last_activity_end_time and (activity_start - last_activity_end_time) > 0.001: # Check for a meaningful gap
                        idle_start = last_activity_end_time
                        idle_duration = activity_start - last_activity_end_time
                        ax.broken_barh(
                            [(idle_start, idle_duration)],
                            (machine.machine_id - 0.4, 0.8),
                            facecolors=idle_color,
                            edgecolor='black',
                            hatch='////'
                        )
                        ax.text(
                            idle_start + idle_duration / 2.0,
                            machine.machine_id,
                            'Idle',
                            rotation=90,
                            ha='center',
                            va='center',
                            fontsize=7,
                            color='grey'
                        )

                    # Plot the current activity (operation, setup, or teardown)
                    color = None
                    label = ""
                    
                    if activity_type == 'operation':
                        op = activity['data']
                        color_index = op.job_id + 2
                        if color_index >= colormap.N:
                            color_index = color_index % colormap.N
                        color = colormap(color_index)
                        label = f"O{op.operation_id}_J{op.job_id}"
                    elif activity_type == 'setup':
                        color = colormap(0) # Color for setup
                        label = "Setup"
                    elif activity_type == 'teardown':
                        color = colormap(1) # Color for teardown
                        label = "Teardown"

                    ax.broken_barh(
                        [(activity_start, activity_duration)],
                        (machine.machine_id - 0.4, 0.8),
                        facecolors=color,
                        edgecolors='black'
                    )

                    # Add text label for the activity
                    ax.text(
                        activity_start + activity_duration / 2.0,
                        machine.machine_id,
                        label,
                        rotation=90,
                        ha='center',
                        va='center',
                        fontsize=8
                    )
                    
                    last_activity_end_time = activity_end # Update for the next idle calculation

                # Handle potential idle time at the end of a machine's active period
                # if there's space between the last activity and the machine's stop_time
                if machine_period_end > last_activity_end_time and (machine_period_end - last_activity_end_time) > 0.001:
                    idle_start = last_activity_end_time
                    idle_duration = machine_period_end - last_activity_end_time
                    ax.broken_barh(
                        [(idle_start, idle_duration)],
                        (machine.machine_id - 0.4, 0.8),
                        facecolors=idle_color,
                        edgecolor='black',
                        hatch='////'
                    )
                    ax.text(
                        idle_start + idle_duration / 2.0,
                        machine.machine_id,
                        'Idle',
                        rotation=90,
                        ha='center',
                        va='center',
                        fontsize=7,
                        color='grey'
                    )


        fig = ax.figure
        fig.set_size_inches(12, 6)

        ax.set_yticks(range(self.inst.nb_machines))
        ax.set_yticklabels([f'M{machine_id+1}' for machine_id in range(self.inst.nb_machines)])
        ax.set_xlabel('Time')
        ax.set_ylabel('Machine')
        ax.set_title('Gantt Chart with Idle Times')
        ax.grid(True)
        ax.set_xlim(left=0) # Ensure the plot starts from 0 or appropriate minimum time

        return plt

