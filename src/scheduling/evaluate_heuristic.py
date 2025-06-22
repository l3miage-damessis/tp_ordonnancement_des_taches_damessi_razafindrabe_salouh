import time
import os

from src.scheduling.instance.instance import Instance
from src.scheduling.optim.constructive import Greedy, NonDeterminist
from src.scheduling.optim.local_search import BestNeighborLocalSearch, FirstNeighborLocalSearch
from src.scheduling.optim.neighborhoods import MyNeighborhood1, MyNeighborhood2
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA



def evaluate_heuristic(heur_class, instance, nb_runs=5, *heur_args):
    """
    Exécute l'heuristique heur_class nb_runs fois sur instance.
    heur_args sont les arguments supplémentaires passés à heur_class.run (après instance).

    Retourne :
    - best_solution : la meilleure solution trouvée sur les runs
    - best_eval : valeur objective de la meilleure solution
    - avg_time : temps moyen d'exécution (en secondes)
    """
    best_solution = None
    best_eval = float('inf')
    total_time = 0.0

    for i in range(nb_runs):
        start = time.time()
        if heur_class in [FirstNeighborLocalSearch, BestNeighborLocalSearch]:
            sol = heur_class().run(instance, NonDeterminist, *heur_args)
        else:
            sol = heur_class().run(instance, {})
            
        elapsed = time.time() - start
        total_time += elapsed

        if sol.evaluate < best_eval:
            best_eval = sol.evaluate
            best_solution = sol

        print(f"Run {i+1}/{nb_runs} finished in {elapsed:.3f}s, solution evaluation: {sol.evaluate}")
        
    avg_time = total_time / nb_runs
    return best_solution, best_eval, avg_time


def main():
    # Chargement de l'instance
    instance_path = os.path.join(TEST_FOLDER_DATA, "jsp100")
    inst = Instance.from_file(instance_path)

    nb_runs = 5  # nombre d'exécutions pour chaque heuristique

    print("=== Evaluation Greedy ===")
    greedy_sol, greedy_eval, greedy_time = evaluate_heuristic(Greedy, inst, nb_runs)

    print("\n=== Evaluation FirstNeighborLocalSearch (MyNeighborhood1) ===")
    first_neighbor_sol, first_neighbor_eval, first_neighbor_time = evaluate_heuristic(
        FirstNeighborLocalSearch, inst, nb_runs, MyNeighborhood1)

    print("\n=== Evaluation BestNeighborLocalSearch (MyNeighborhood1 + MyNeighborhood2) ===")
    best_neighbor_sol, best_neighbor_eval, best_neighbor_time = evaluate_heuristic(
        BestNeighborLocalSearch, inst, nb_runs, MyNeighborhood1, MyNeighborhood2)

    print("\n--- Résultats comparatifs ---")
    print(f"Greedy : meilleure évaluation = {greedy_eval:.3f}, temps moyen = {greedy_time:.3f}s")
    print(f"FirstNeighborLocalSearch (1 voisinage) : meilleure évaluation = {first_neighbor_eval:.3f}, temps moyen = {first_neighbor_time:.3f}s")
    print(f"BestNeighborLocalSearch (2 voisinages) : meilleure évaluation = {best_neighbor_eval:.3f}, temps moyen = {best_neighbor_time:.3f}s")

    # Optionnel : sauvegarde des diagrammes de Gantt des meilleures solutions
    if greedy_sol is None:
        print("Warning: heuristic returned None solution")
    greedy_sol.gantt("tab20").savefig("gantt_greedy_evaluate_heuristic.png")
    print("Gantt Greedy sauvegardé : gantt_greedy_evaluate_heuristic.png")

    first_neighbor_sol.gantt("tab20").savefig("gantt_first_neighbor_evaluate_heuristic.png")
    print("Gantt FirstNeighborLocalSearch sauvegardé : gantt_first_neighbor_evaluate_heuristic.png")

    best_neighbor_sol.gantt("tab20").savefig("gantt_best_neighbor_evaluate_heuristic.png")
    print("Gantt BestNeighborLocalSearch sauvegardé : gantt_best_neighbor_evaluate_heuristic.png")


if __name__ == "__main__":
    main()
