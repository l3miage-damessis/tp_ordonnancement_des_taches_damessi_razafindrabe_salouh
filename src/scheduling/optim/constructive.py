'''
Constructive heuristics that returns preferably **feasible** solutions.

@author: Vassilissa Lehoux
'''
from typing import Dict, List, Tuple
import random

from src.scheduling.instance.instance import Instance
from src.scheduling.instance.machine import Machine
from src.scheduling.instance.operation import Operation
from src.scheduling.solution import Solution
from src.scheduling.optim.heuristics import Heuristic
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA
import os

class Greedy(Heuristic):
    """
    Greedy heuristic: at each step, selects the ready operation 
    with the admissible machine minimizing a local cost function 
    (duration + energy).

    Attributes:
        alpha (float): Weight coefficient for duration in cost function.
        beta (float): Weight coefficient for energy in cost function.
    """

    def __init__(self, params: Dict = dict()):
        super().__init__(params)
        self.alpha = self.params.get("alpha", 1.0)
        self.beta = self.params.get("beta", 1.0)

    def _should_shutdown(self, machine: Machine, idle_gap: int) -> bool:
        """
        Decide whether the machine should be shut down during a given idle gap.

        Args:
            machine (Machine): The machine to evaluate.
            idle_gap (int): Idle time interval length.

        Returns:
            bool: True if shutting down is more energy-efficient than staying idle.
        """
        # If idle gap is shorter than combined setup and teardown time, keep machine on
        if idle_gap <= machine.set_up_time + machine.tear_down_time:
            return False

        idle_energy = idle_gap * machine._min_consumption
        switch_energy = machine._set_up_energy + machine._tear_down_energy
        return switch_energy < idle_energy

    def run(self, instance: Instance, params: Dict = dict()) -> Solution:
        """
        Build a schedule by iteratively selecting the operation-machine pair 
        with the minimal local cost.

        Args:
            instance (Instance): Problem instance to solve.
            params (Dict, optional): Additional parameters (unused here).

        Returns:
            Solution: A feasible schedule constructed greedily.
        """
        solution = Solution(instance)
        planned_operations = 0
        total_operations = instance.nb_operations

        while planned_operations < total_operations:
            available_ops = solution.available_operations

            if not available_ops:
                # No operations ready, stop active machines to save energy
                for machine in instance.machines():
                    if machine.active:
                        machine.stop(machine.available_time)
                continue

            best_option = None
            min_cost = float('inf')

            for op in available_ops:
                for machine_id, (duration, energy) in op._machine_options.items():
                    machine = instance.get_machine(machine_id)

                    precedence_time = op.min_start_time
                    machine_ready_time = machine.available_time

                    # Account for machine setup time if inactive
                    if not machine.active:
                        setup_start = max(precedence_time, machine_ready_time)
                        machine_ready_after_setup = setup_start + machine.set_up_time
                    else:
                        machine_ready_after_setup = max(precedence_time, machine_ready_time)

                    cost = self.alpha * duration + self.beta * energy

                    if cost < min_cost:
                        min_cost = cost
                        best_option = (op, machine, machine_ready_after_setup, duration)

            if best_option is None:
                print("Error: no valid machine found for ready operations.")
                break

            chosen_op, chosen_machine, start_time, duration = best_option

            last_op = chosen_machine.scheduled_operations[-1] if chosen_machine.scheduled_operations else None
            if last_op:
                gap = start_time - last_op.end_time
                if chosen_machine.active and self._should_shutdown(chosen_machine, gap):
                    try:
                        chosen_machine.stop(last_op.end_time)
                    except AssertionError:
                        pass

            solution.schedule(chosen_op, chosen_machine)
            planned_operations += 1

        # Stop any remaining active machines at the end of the schedule
        for machine in instance.machines:
            if machine.active:
                machine.stop(machine.available_time)

        return solution
    
class NonDeterminist(Heuristic):
    '''
    Non-deterministic heuristic that builds a solution by randomly assigning 
    each ready operation to one of its admissible machines.
    '''

    def __init__(self, params: Dict = dict()):
        '''
        Constructor
        @param params: Dictionary of parameters. May include 'seed' for RNG reproducibility.
        '''
        super().__init__(params)
        seed = self.params.get("seed", None)
        if seed is not None:
            random.seed(seed)

    def _should_shutdown(self, machine: Machine, idle_gap: int) -> bool:
        """
        Decide whether the machine should be shut down during a given idle gap.

        Args:
            machine (Machine): The machine to evaluate.
            idle_gap (int): Idle time interval length.

        Returns:
            bool: True if shutting down is more energy-efficient than staying idle.
        """
        if idle_gap <= machine.set_up_time + machine.tear_down_time:
            return False
        idle_energy = idle_gap * machine._min_consumption
        switch_energy = machine._set_up_energy + machine._tear_down_energy
        return switch_energy < idle_energy

    def run(self, instance: Instance, params: Dict = dict()) -> Solution:
        '''
        Build a schedule by randomly assigning ready operations to admissible machines.

        Args:
            instance (Instance): Problem instance to solve.
            params (Dict): Optional parameters (can override seed etc).

        Returns:
            Solution: A feasible schedule constructed randomly.
        '''
        # Update parameters with runtime ones
        current_params = {**self.params, **params}

        solution = Solution(instance)
        planned_operations = 0
        total_operations = instance.nb_operations

        while planned_operations < total_operations:
            available_ops = solution.available_operations

            if not available_ops:
                # No operations ready, stop active machines to save energy
                for machine in instance.machines:
                    if machine.active:
                        machine.stop(machine.available_time)
                continue

            # Randomly pick one operation among available ones
            op = random.choice(available_ops)

            # Gather admissible machines for this operation
            admissible_machines = []
            for machine_id, (duration, energy) in op._machine_options.items():
                machine = instance.get_machine(machine_id)
                admissible_machines.append((machine, duration, energy))

            if not admissible_machines:
                # No admissible machine found for this operation
                raise RuntimeError(f"No admissible machine found for operation {op}")

            # Randomly choose one admissible machine
            chosen_machine, duration, energy = random.choice(admissible_machines)

            # Determine earliest feasible start time
            precedence_time = op.min_start_time
            machine_ready_time = chosen_machine.available_time

            if not chosen_machine.active:
                setup_start = max(precedence_time, machine_ready_time)
                machine_ready_after_setup = setup_start + chosen_machine.set_up_time
            else:
                machine_ready_after_setup = max(precedence_time, machine_ready_time)

            # Check if machine should be shut down between last operation and this start
            last_op = chosen_machine.scheduled_operations[-1] if chosen_machine.scheduled_operations else None
            if last_op:
                gap = machine_ready_after_setup - last_op.end_time
                if chosen_machine.active and self._should_shutdown(chosen_machine, gap):
                    try:
                        chosen_machine.stop(last_op.end_time)
                    except AssertionError:
                        pass

            # Schedule the operation
            solution.schedule(op, chosen_machine)
            planned_operations += 1

        # Stop any remaining active machines at the end of the schedule
        for machine in instance.machines:
            if machine.active:
                machine.stop(machine.available_time)

        return solution
    
if __name__ == "__main__":
    # Example of playing with the heuristics
    inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
    heurGreedy = Greedy(params={'alpha_local': 1.0, 'beta_local': 1.0})
    solGreedy = heurGreedy.run(inst)
    pltGreedy = solGreedy.gantt("tab20")
    solGreedy.to_csv()
    pltGreedy.savefig("ganttGreedyConstructive.png")
    heurNonDeterminist = NonDeterminist()
    solNonDeterminist = heurNonDeterminist.run(inst)
    pltNonDeterminist = solNonDeterminist.gantt("tab20")
    pltNonDeterminist.savefig("ganttNonDeterministConstructive.png")
