'''
Neighborhoods for solutions.
They must derive from the Neighborhood class.

@author: Vassilissa Lehoux
'''
import copy
from typing import Dict, List, Optional

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


class MyNeighborhood1(Neighborhood):
    """
    Neighborhood that explores solutions by moving operations to different machines 
    (among their allowed machine options). After each move, it locally repairs the schedules 
    of both source and target machines to preserve feasibility.

    This neighborhood is useful for escaping local optima by reassigning operations while 
    ensuring job and machine constraints are maintained.
    """

    def __init__(self, instance: Instance, params: Dict = dict()):
        super().__init__(instance, params)

    def _repair_machine_schedule(self, sol: Solution, machine: Machine, operations: List[Operation]):
        """
        Resets a machine and reschedules the given operations in their original relative order.
        This maintains intra-machine sequencing and ensures feasibility.
        """
        ordered_ops = sorted(operations, key=lambda op: op.start_time)

        for op in operations:
            op.reset()
        machine.reset()

        for op in ordered_ops:
            sol.schedule(op, machine)

    def _try_move_and_repair(self, sol: Solution, op: Operation,
                             src_id: int, tgt_id: int) -> bool:
        """
        Attempt to move an operation to a different machine and repair the affected schedules.

        Args:
            sol: The solution to modify.
            op: The operation to move.
            src_id: ID of the source machine.
            tgt_id: ID of the target machine.

        Returns:
            True if the operation was successfully moved and the resulting solution is feasible.
        """
        src = sol.inst.get_machine(src_id)
        tgt = sol.inst.get_machine(tgt_id)

        if not src or not tgt or tgt_id not in op.machine_options:
            return False

        try:
            # Unschedule the operation and repair the source machine schedule
            remaining_src_ops = [o for o in src.scheduled_operations if o.operation_id != op.operation_id]
            sol.unschedule(op)
            self._repair_machine_schedule(sol, src, remaining_src_ops)

            # Schedule operation on the target machine
            sol.schedule(op, tgt)

            # Rebuild target machine schedule including the new operation
            target_ops = list(tgt.scheduled_operations)
            if op not in target_ops:
                target_ops.append(op)

            target_ops.sort(key=lambda o: (o.job_id, o.operation_id))
            self._repair_machine_schedule(sol, tgt, target_ops)

            if sol.is_feasible:
                print(f"Move succeeded: job={op.job_id}, op={op.operation_id}, from M{src_id} to M{tgt_id}, eval={sol.evaluate}")
                return True
            else:
                return False
        except Exception as e:
            print(f"Move operation failed: {e}")
            return False

    def _attempt_all_moves(self, sol: Solution, stop_on_first: bool = False) -> Optional[Solution]:
        """
        Explore moving each operation to all admissible machines.

        Args:
            sol: The current solution.
            stop_on_first: Whether to stop at the first improving neighbor.

        Returns:
            A new solution if an improving move is found (based on stop_on_first),
            otherwise None.
        """
        best_sol = None
        best_eval = sol.evaluate

        for op in sol.all_operations:
            current_id = op.assigned_to
            if current_id == -1:
                continue

            for machine in self._instance.machines:
                target_id = machine.machine_id
                if target_id == current_id or target_id not in op.machine_options:
                    continue

                new_sol = copy.deepcopy(sol)
                moved_op = next(
                    (o for o in new_sol.all_operations 
                     if o.operation_id == op.operation_id and o.job_id == op.job_id),
                    None
                )
                if not moved_op:
                    continue

                if self._try_move_and_repair(new_sol, moved_op, current_id, target_id):
                    if new_sol.evaluate < best_eval:
                        if stop_on_first:
                            print("[MyNeighborhood1] Nouvelle solution meilleure trouvée (OperationMove): " + str(new_sol))
                            return new_sol
                        best_sol = new_sol
                        best_eval = new_sol.evaluate

        return best_sol

    def best_neighbor(self, sol: Solution) -> Solution:
        """
        Explore all possible operation moves and return the best improving neighbor.
        """
        neighbor = self._attempt_all_moves(sol, stop_on_first=False)
        return neighbor if neighbor else sol

    def first_better_neighbor(self, sol: Solution) -> Solution:
        """
        Return the first found neighbor that improves the objective function.
        """
        neighbor = self._attempt_all_moves(sol, stop_on_first=True)
        if neighbor:
            print(f"[MyNeighborhood1] Premier meilleur voisinage trouvé : évaluation améliorée de {sol.evaluate:.2f} à {neighbor.evaluate:.2f}")
            return neighbor

        print("[MyNeighborhood1] Aucune meilleure solution trouvée avec MyNeighborhood1 (OperationMove).")
        return sol

class MyNeighborhood2(Neighborhood):
    """
    Neighborhood that explores solutions by swapping two operations between different machines,
    when each operation is allowed to run on the machine of the other.

    The neighborhood ensures feasibility after each swap by repairing the schedules of both 
    involved machines. Useful for exploring alternative machine assignments while preserving 
    operation sequences and precedence constraints.
    """

    def __init__(self, instance: Instance, params: Dict = dict()):
        super().__init__(instance, params)

    def _repair_machine_schedule(self, sol: Solution, machine: Machine, operations: List[Operation]):
        """
        Reset the given machine and reschedule the provided operations in a consistent order.
        The rescheduling attempts to maintain job order and operation availability.
        """
        ordered_ops = sorted(operations, key=lambda op: (op.job_id, op.operation_id))

        for op in operations:
            op.reset()
        machine.reset()

        for op in ordered_ops:
            if machine.machine_id in op.machine_options:
                try:
                    sol.schedule(op, machine)
                except ValueError:
                    pass  # Let feasibility check handle any violations

    def _try_swap_and_repair(self, sol: Solution, op1: Operation, op2: Operation) -> bool:
        """
        Try swapping the machines of op1 and op2, and repair the schedules of both machines.

        Returns True if the resulting solution is feasible after the swap and repairs.
        """
        m1_id, m2_id = op1.assigned_to, op2.assigned_to
        m1, m2 = sol.inst.get_machine(m1_id), sol.inst.get_machine(m2_id)

        if not m1 or not m2:
            return False
        if m2_id not in op1.machine_options or m1_id not in op2.machine_options:
            return False

        try:
            # Unschedule the operations
            ops_m1 = [o for o in m1.scheduled_operations if o.operation_id != op1.operation_id]
            ops_m2 = [o for o in m2.scheduled_operations if o.operation_id != op2.operation_id]

            sol.unschedule(op1)
            sol.unschedule(op2)

            self._repair_machine_schedule(sol, m1, ops_m1)
            self._repair_machine_schedule(sol, m2, ops_m2)

            # Assign to new machines
            sol.schedule(op1, m2)
            sol.schedule(op2, m1)

            # Final repair on both machines with all operations
            if op2 not in m1.scheduled_operations:
                m1.scheduled_operations.append(op2)
            if op1 not in m2.scheduled_operations:
                m2.scheduled_operations.append(op1)

            self._repair_machine_schedule(sol, m1, m1.scheduled_operations)
            self._repair_machine_schedule(sol, m2, m2.scheduled_operations)

            if sol.is_feasible:
                print(f"Swap succeeded: job{op1.job_id}.op{op1.operation_id} <--> job{op2.job_id}.op{op2.operation_id} "
                    f"between M{m1_id} and M{m2_id}, eval={sol.evaluate}")
                return True
            else:
                return False
        except Exception as e:
            print(f"Swap operations failed: {e}")
            return False

    def _attempt_all_swaps(self, sol: Solution, stop_on_first: bool = False) -> Optional[Solution]:
        """
        Explore all valid operation swaps between distinct machines.

        Args:
            sol: The base solution.
            stop_on_first: If True, stop at first improving neighbor.

        Returns:
            An improved solution or None if no improvement found.
        """
        best_sol = None
        best_eval = sol.evaluate
        ops = sol.all_operations
        n = len(ops)

        for i in range(n):
            op1 = ops[i]
            if not op1.assigned:
                continue

            for j in range(i + 1, n):
                op2 = ops[j]
                if not op2.assigned or op1.assigned_to == op2.assigned_to:
                    continue

                new_sol = copy.deepcopy(sol)

                new_op1 = next((o for o in new_sol.all_operations if o.operation_id == op1.operation_id and o.job_id == op1.job_id), None)
                new_op2 = next((o for o in new_sol.all_operations if o.operation_id == op2.operation_id and o.job_id == op2.job_id), None)
                if not new_op1 or not new_op2:
                    continue

                if self._try_swap_and_repair(new_sol, new_op1, new_op2):
                    if new_sol.evaluate < best_eval:
                        if stop_on_first:
                            print("[MyNeighborhood2] Nouvelle solution meilleure trouvée (OperationSwap): " + str(new_sol))
                            return new_sol
                        best_sol = new_sol
                        best_eval = new_sol.evaluate

        return best_sol

    def best_neighbor(self, sol: Solution) -> Solution:
        """
        Return the best improving neighbor obtained by swapping two operations between machines.
        """
        neighbor = self._attempt_all_swaps(sol, stop_on_first=False)
        return neighbor if neighbor else sol

    def first_better_neighbor(self, sol: Solution) -> Solution:
        """
        Return the first improving neighbor found by a valid swap between operations.
        """
        neighbor = self._attempt_all_swaps(sol, stop_on_first=True)
        if neighbor:
            print(f"[MyNeighborhood2] Premier meilleur voisinage trouvé : évaluation améliorée de {sol.evaluate:.2f} à {neighbor.evaluate:.2f}")
            return neighbor

        print("[MyNeighborhood2] Aucune meilleure solution trouvée avec MyNeighborhood2 (OperationSwap).")
        return sol
