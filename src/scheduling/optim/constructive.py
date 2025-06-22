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
    
# # class NonDeterminist(Heuristic):
# #     '''
# #     Heuristic that returns different values for different runs with the same parameters
# #     (or different values for different seeds and otherwise same parameters)
# #     '''

# #     def __init__(self, params: Dict=dict()):
# #         '''
# #         Constructor
# #         @param params: The parameters of your heuristic method if any as a
# #                dictionary. Implementation should provide default values in the function.
# #         '''
# #         raise "Not implemented error"

# #     def run(self, instance: Instance, params: Dict=dict()) -> Solution:
# #         '''
# #         Computes a solution for the given instance.
# #         Implementation should provide default values in the function
# #         (the function will be evaluated with an empty dictionary).

# #         @param instance: the instance to solve
# #         @param params: the parameters for the run
# #         '''
# #         raise "Not implemented error"


# class NonDeterminist(Heuristic):
#     """
#     Heuristic that returns different solutions at each execution.
#     Randomized scheduling among top-k earliest finish time candidates.
#     """

#     def __init__(self, params: Dict = dict()):
#         super().__init__(params)
#         self.params.setdefault('selection_pool_size', 0.2)  # Top-k% selection pool
#         self.params.setdefault('seed', None)  # Optional seed for reproducibility

#     def run(self, instance: Instance, params: Dict = dict()) -> Solution:
#         current_params = {**self.params, **params}

#         # Graine : générée automatiquement si absente
#         seed = current_params.get('seed')
#         if seed is None:
#             seed = int.from_bytes(os.urandom(8), 'big')
#             print(f"[NonDeterminist] Random seed (auto-generated): {seed}")
#         else:
#             print(f"[NonDeterminist] Using provided seed: {seed}")
#         random.seed(seed)

#         solution = Solution(instance)
#         total_operations = instance.nb_operations
#         scheduled_operations = 0

#         while scheduled_operations < total_operations:
#             ready_operations = list(solution.available_operations)
#             if not ready_operations:
#                 print("Warning: Deadlock or unfeasible instance detected.")
#                 break

#             random.shuffle(ready_operations) 

#             options: List[Tuple[Operation, Machine, float, float]] = []

#             for op in ready_operations:
#                 machine_ids = list(op._machine_options.keys())
#                 random.shuffle(machine_ids) 
#                 for m_id in machine_ids:
#                     duration, _ = op._machine_options[m_id]
#                     machine = instance.get_machine(m_id)

#                     job_ready = op.min_start_time
#                     machine_ready = machine.available_time

#                     if machine.active:
#                         start_time = max(job_ready, machine_ready)
#                     else:
#                         setup_ready = max(machine_ready, job_ready - machine.set_up_time) + machine.set_up_time
#                         start_time = max(job_ready, setup_ready)

#                     end_time = start_time + duration
#                     options.append((op, machine, start_time, end_time))

#             if not options:
#                 print("Error: No scheduling options available.")
#                 break

#             options.sort(key=lambda x: x[3])
#             k = max(1, int(len(options) * current_params['selection_pool_size']))
#             selection_pool = options[:k]

#             op, machine, start_time, end_time = random.choice(selection_pool)

#             solution.schedule(op, machine)
#             scheduled_operations += 1

#             for machine in instance.machines:
#                 ops = sorted(machine.scheduled_operations, key=lambda op: op.start_time)
#                 for i in range(len(ops) - 1):
#                     end_i = ops[i].end_time
#                     start_j = ops[i+1].start_time
#                     gap = start_j - end_i

#                     if gap > machine.tear_down_time + machine.set_up_time:
#                         energy_cost = machine.tear_down_energy + machine.set_up_energy
#                         energy_saving = gap * machine.min_consumption

#                         if energy_cost < energy_saving and machine.active:
#                             machine.stop(end_i)


#         for machine in instance.machines:
#             if machine.active:
#                 machine.stop(machine.available_time)

#         return solution

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
    pltGreedy.savefig("ganttGreedy.png")
    heurNonDeterminist = NonDeterminist()
    solNonDeterminist = heurNonDeterminist.run(inst)
    pltNonDeterminist = solNonDeterminist.gantt("tab20")
    pltNonDeterminist.savefig("ganttNonDeterminist.png")
