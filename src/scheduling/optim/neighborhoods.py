'''
Neighborhoods for solutions.
They must derive from the Neighborhood class.

@author: Vassilissa Lehoux
'''
import copy
from typing import Dict

from src.scheduling.instance.instance import Instance
from src.scheduling.instance.machine import Machine
from src.scheduling.instance.operation import Operation
from src.scheduling.solution import Solution


class Neighborhood(object):
    '''
    Base neighborhood class for solutions of a given instance.
    Do not modify!!!
    '''

    def __init__(self, instance: Instance, params: Dict=dict()):
        '''
        Constructor
        '''
        self._instance = instance

    def best_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the best solution in the neighborhood of the solution.
        Can be the solution itself.
        '''
        raise "Not implemented error"

    def first_better_neighbor(self, sol: Solution):
        '''
        Returns the first solution in the neighborhood of the solution
        that improves other it and the solution itself if none is better.
        '''
        raise "Not implemented error"

# class MyNeighborhood1(Neighborhood):
#     '''
#     Neighborhood by swapping two operations on the same machine.
#     Swap operations and check if solution improves.
#     '''

#     def __init__(self, instance: Instance, params: Dict = dict()):
#         super().__init__(instance, params)

#     def best_neighbor(self, sol: Solution) -> Solution:
#         best_sol = sol
#         best_eval = sol.evaluate

#         for machine in self._instance.machines:
#             ops = sorted(machine.scheduled_operations, key=lambda o: o.start_time)
#             n = len(ops)
#             for i in range(n):
#                 for j in range(i + 1, n):
#                     new_sol = copy.deepcopy(sol)  # deepcopy total pour isoler la solution
#                     if self._try_swap(new_sol, machine, ops[i], ops[j]):
#                         if new_sol.is_feasible and new_sol.evaluate < best_eval:
#                             best_sol = new_sol
#                             best_eval = new_sol.evaluate
#         print("celui ci")
#         return best_sol

#     def first_better_neighbor(self, sol: Solution) -> Solution:
#         print("solution initiale en entrée " + str(sol))
#         for machine in self._instance.machines:
#             ops = sorted(machine.scheduled_operations, key=lambda o: o.start_time)
#             n = len(ops)
#             for i in range(n):
#                 for j in range(i + 1, n):
#                     new_sol = copy.deepcopy(sol)
#                     if self._try_swap(new_sol, machine, ops[i], ops[j]):
#                         if new_sol.is_feasible and new_sol.evaluate < sol.evaluate:
#                             print("new_sol  " + str(new_sol))
#                             return new_sol
        
#         print("solution initiale avant return  " + str(sol))
#         return sol

#     def _try_swap(self, sol: Solution, machine: Machine, op1: Operation, op2: Operation) -> bool:
#         # Unschedule both operations
#         op1.reset()
#         op2.reset()

#         try:
#             # Schedule the swapped operations in swapped order
#             sol.schedule(op2, machine)
#             sol.schedule(op1, machine)
#         except Exception:
#             return False

#         return sol.is_feasible

import copy
# class MyNeighborhood1(Neighborhood):
#     """
#     Neighborhood that swaps two operations on the same machine.
#     """

#     def __init__(self, instance: Instance, params: Dict = dict()):
#         super().__init__(instance, params)

#     def best_neighbor(self, sol: Solution) -> Solution:
#         best_sol = sol
#         best_eval = sol.evaluate

#         for machine in self._instance.machines:
#             ops = sorted(machine.scheduled_operations, key=lambda o: o.start_time)
#             n = len(ops)
#             for i in range(n):
#                 for j in range(i + 1, n):
#                     new_sol = copy.deepcopy(sol)
#                     new_machine = new_sol.inst.get_machine(machine.machine_id)

#                     # Find operations by ID to avoid mismatches
#                     new_ops = sorted(new_machine.scheduled_operations, key=lambda o: o.start_time)
#                     new_op1 = next(op for op in new_ops if op.operation_id == ops[i].operation_id)
#                     new_op2 = next(op for op in new_ops if op.operation_id == ops[j].operation_id)

#                     if self._try_swap(new_sol, new_machine, new_op1, new_op2):
#                         if new_sol.is_feasible and new_sol.evaluate < best_eval:
#                             best_sol = new_sol
#                             best_eval = new_sol.evaluate
#         return best_sol

#     def first_better_neighbor(self, sol: Solution) -> Solution:
#         print("Initial solution:\n", str(sol))
#         for machine in self._instance.machines:
#             ops = sorted(machine.scheduled_operations, key=lambda o: o.start_time)
#             n = len(ops)
#             for i in range(n):
#                 for j in range(i + 1, n):
#                     new_sol = copy.deepcopy(sol)
#                     new_machine = new_sol.inst.get_machine(machine.machine_id)

#                     new_ops = sorted(new_machine.scheduled_operations, key=lambda o: o.start_time)
#                     new_op1 = next(op for op in new_ops if op.operation_id == ops[i].operation_id)
#                     new_op2 = next(op for op in new_ops if op.operation_id == ops[j].operation_id)

#                     if self._try_swap(new_sol, new_machine, new_op1, new_op2):
#                         if new_sol.is_feasible and new_sol.evaluate < sol.evaluate:
#                             return new_sol
#         print("Returning initial solution:\n", str(sol))
#         return sol

#     def _try_swap(self, sol: Solution, machine: Machine, op1: Operation, op2: Operation) -> bool:
#         """
#         Swap two operations on the same machine in the solution.
#         Returns True if feasible.
#         """
#         try:
#             print("operations :" + str(machine.scheduled_operations))
#             print("operations :" + str(machine.scheduled_operations))
#             print("op1 avant:" + str(op1))
#             print("op2 avant:" + str(op2))
#             sol.unschedule(op1)
#             sol.unschedule(op2)
#             sol.schedule(op2, machine)
#             sol.schedule(op1, machine)
#             print("operations :" + str(machine.scheduled_operations))
#             print("op1 après:" + str(op1))
#             print("op2 après:" + str(op2))
#         except Exception as e:
#             print(f"Exception during swap: {e}")
#             return False

#         if not sol.is_feasible:
#             print(f"Infeasible after swap: {op1.operation_id}, {op2.operation_id}")
#         return sol.is_feasible


class MyNeighborhood1(Neighborhood):
    """
    Neighborhood that swaps two operations on the same machine and replans the machine schedule.
    """

    def __init__(self, instance: Instance, params: Dict = dict()):
        super().__init__(instance, params)

    def best_neighbor(self, sol: Solution) -> Solution:
        best_sol = sol
        best_eval = sol.evaluate

        for machine in self._instance.machines:
            ops = sorted(machine.scheduled_operations, key=lambda o: o.start_time)
            n = len(ops)
            for i in range(n):
                for j in range(i + 1, n):
                    new_sol = copy.deepcopy(sol)
                    new_machine = new_sol.inst.get_machine(machine.machine_id)

                    # Récupérer les opérations correspondantes dans la copie
                    new_ops = sorted(new_machine.scheduled_operations, key=lambda o: o.start_time)
                    op1 = next(op for op in new_ops if op.operation_id == ops[i].operation_id and op.job_id == ops[i].job_id)
                    op2 = next(op for op in new_ops if op.operation_id == ops[j].operation_id and op.job_id == ops[j].job_id)

                    # Swap et replanning local
                    if self._swap_and_repair(new_sol, new_machine, op1, op2):
                        if new_sol.is_feasible and new_sol.evaluate < best_eval:
                            best_sol = new_sol
                            best_eval = new_sol.evaluate
        return best_sol

    def first_better_neighbor(self, sol: Solution) -> Solution:
        for machine in self._instance.machines:
            ops = sorted(machine.scheduled_operations, key=lambda o: o.start_time)
            n = len(ops)
            for i in range(n):
                for j in range(i + 1, n):
                    new_sol = copy.deepcopy(sol)
                    new_machine = new_sol.inst.get_machine(machine.machine_id)

                    new_ops = sorted(new_machine.scheduled_operations, key=lambda o: o.start_time)
                    op1 = next(op for op in new_ops if op.operation_id == ops[i].operation_id and op.job_id == ops[i].job_id)
                    op2 = next(op for op in new_ops if op.operation_id == ops[j].operation_id and op.job_id == ops[j].job_id)

                    if self._swap_and_repair(new_sol, new_machine, op1, op2):
                        if new_sol.is_feasible and new_sol.evaluate < sol.evaluate:
                            return new_sol
        return sol

    def _swap_and_repair(self, sol: Solution, machine: Machine, op1: Operation, op2: Operation) -> bool:
        try:
            # Retirer toutes les opérations de la machine
            scheduled_ops = sorted(machine.scheduled_operations, key=lambda o: o.start_time)
            for op in scheduled_ops:
                op.reset()
            machine.reset()

            # Effectuer le swap dans la liste
            scheduled_ops = [op for op in scheduled_ops if op != op1 and op != op2]
            i1 = i2 = -1
            for idx, op in enumerate(machine.scheduled_operations):
                if op.operation_id == op1.operation_id and op.job_id == op1.job_id:
                    i1 = idx
                elif op.operation_id == op2.operation_id and op.job_id == op2.job_id:
                    i2 = idx

            if i1 == -1 or i2 == -1:
                return False

            # Swap dans la liste reconstituée
            new_sequence = scheduled_ops.copy()
            new_sequence.insert(min(i1, i2), op2 if i1 < i2 else op1)
            new_sequence.insert(max(i1, i2), op1 if i1 < i2 else op2)

            # Réinitialiser la machine avant replanning
            machine.reset()

            # Replanifier toute la machine avec la nouvelle séquence
            for op in new_sequence:
                sol.schedule(op, machine)

            return sol.is_feasible
        except Exception as e:
            print(f"Swap failed with exception: {e}")
            return False

class MyNeighborhood2(Neighborhood):
    '''
    Neighborhood by moving one operation from one machine to another.
    Replans both machines locally after the move.
    '''

    def __init__(self, instance: Instance, params: Dict = dict()):
        super().__init__(instance, params)

    def best_neighbor(self, sol: Solution) -> Solution:
        best_sol = sol
        best_eval = sol.evaluate

        for src_machine in self._instance.machines:
            ops = list(src_machine.scheduled_operations)

            for op in ops:
                for tgt_machine in self._instance.machines:
                    if tgt_machine.machine_id == src_machine.machine_id:
                        continue

                    new_sol = copy.deepcopy(sol)

                    new_src = new_sol.instance.get_machine(src_machine.machine_id)
                    new_tgt = new_sol.instance.get_machine(tgt_machine.machine_id)

                    new_op = next((o for o in new_src.scheduled_operations if o.operation_id == op.operation_id), None)
                    if new_op is None:
                        continue

                    if self._try_move_and_repair(new_sol, new_op, new_src, new_tgt):
                        if new_sol.is_feasible and new_sol.evaluate < best_eval:
                            best_sol = new_sol
                            best_eval = new_sol.evaluate

        return best_sol

    def first_better_neighbor(self, sol: Solution) -> Solution:
        print("Solution initiale : " + str(sol))
        for src_machine in self._instance.machines:
            ops = list(src_machine.scheduled_operations)

            for op in ops:
                for tgt_machine in self._instance.machines:
                    if tgt_machine.machine_id == src_machine.machine_id:
                        continue

                    new_sol = copy.deepcopy(sol)

                    new_src = new_sol.inst.get_machine(src_machine.machine_id)
                    new_tgt = new_sol.inst.get_machine(tgt_machine.machine_id)

                    new_op = next((o for o in new_src.scheduled_operations if o.operation_id == op.operation_id), None)
                    if new_op is None:
                        continue

                    if self._try_move_and_repair(new_sol, new_op, new_src, new_tgt):
                        if new_sol.is_feasible and new_sol.evaluate <= sol.evaluate:
                            print("la nouvelle solution est meilleure")
                            return new_sol

        print("Solution finale : " + str(sol))
        return sol

    def _try_move_and_repair(self, sol: Solution, op: Operation, src_machine: Machine, tgt_machine: Machine) -> bool:
        '''
        Try moving an operation from src_machine to tgt_machine and repair both local schedules.
        '''
        try:
            # Remove operation from source and reset
            sol.unschedule(op)

            # Reset and reschedule all operations of both machines
            for machine in [src_machine, tgt_machine]:
                other_ops = [o for o in machine.scheduled_operations if o != op]
                for o in other_ops:
                    o.reset()
                machine.reset()
                for o in sorted(other_ops, key=lambda x: x.job_id):  # Sort policy may vary
                    sol.schedule(o, machine)

            # Now insert the moved op in the new machine
            sol.schedule(op, tgt_machine)

        except Exception as e:
            print("exception : " + str(e))
            return False

        return sol.is_feasible
